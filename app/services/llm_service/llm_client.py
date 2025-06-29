import asyncio
import json
from os import PathLike
from pathlib import Path
from typing import List, Type, TypeVar

from litellm import (
    acreate_batch,
    acreate_file,
    afile_content,
    aretrieve_batch,
    completion,
)

from app.core.config import Settings
import logging
from app.services.llm_service.llm_models import LLMModels

logger = logging.getLogger(__name__)


class LLMClient:
    """
    This takes the LiteLLM Gateway to communicate to any LLM provider

    Parameters:
        model (LLMModels): An enum value representing the language model to
        use. Extend it if you need it
        api_key (Optional[str]): API key for authentication. If None, assumes
        that environment variable is set accordingly
        https://docs.litellm.ai/docs/

    Examples:
        >>> service = LLMClient(LLMModels.GPT_4)
        >>> response = service.generate_response("Tell me a joke")
    """

    def __init__(self, model: LLMModels):
        self.model = model.value
        self.api_key = Settings().get_openai_api_key()

    def generate_response(self, prompt: str, temperature: float = 0.1) -> str:
        return self.__prompt(prompt, temperature=temperature)

    T = TypeVar("T")

    def generate_typed_response(self, prompt: str, resp_format_type: Type[T], temperature: float = 0.1) -> T:
        output = self.__prompt(prompt, resp_format=resp_format_type, temperature=temperature)
        data = json.loads(output)
        return resp_format_type(**data)

    def __prompt(self, prompt: str, resp_format=None, temperature: float = 0.1):
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        if resp_format:
            kwargs["response_format"] = resp_format

        if self.api_key:
            kwargs["api_key"] = self.api_key

        try:
            response = completion(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            logger.exception(
                f"Error occurred while generating response with model \
                '{self.model}': {e}"
            )
            raise

    @staticmethod
    def build_request_jsonl(
        custom_id: str,
        model: str,
        prompt: str,
        temperature: float = 0.1,
    ) -> dict:
        """
        Builds a JSONL-formatted request payload for use with OpenAI's
        batch API.

        Args:
        custom_id (str): unique identifier for the request
        model (str): The name of the LLM model to be used.
        prompt (str): The user prompt to be sent to the model.
        temperature (float, optional): randomness

        Returns:
            dict: dictionary representing a single request payload.
        """
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            },
        }

    @staticmethod
    def generate_batch(
        custom_ids: List[str],
        prompts: List[str],
        model: str,
        temperature: float = 0.1,
        output_filename: str | PathLike[str] = "batch.jsonl",
    ) -> Path | None:
        """
        Generates a batch of request payloads in JSONL format and writes them
        to a file for use with OpenAI's batch API.

        Args:
            custom_ids (List[str]): List of unique identifiers for each prompt.
            prompts (List[str]): List of prompts to send to the model.
            model (str): The name of the LLM model to be used.
            temperature (float, optional): randomness.
            output_filename (Optional[str): Name of the output .jsonl file.

        Returns:
            Path: Path object pointing to the created .jsonl file.
        """
        if len(custom_ids) != len(prompts):
            logger.error("custom_ids must be the same length as prompts")
            return None

        lines = []
        for i in range(len(prompts)):
            request = LLMClient.build_request_jsonl(
                custom_id=custom_ids[i],
                model=model,
                prompt=prompts[i],
                temperature=temperature,
            )
            lines.append(request)

        output_path = Path(output_filename)
        with output_path.open("w", encoding="utf-8") as f:
            for line in lines:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

        logger.info(f"Batch written to {output_path}")
        return output_path

    @staticmethod
    async def upload_batch_file(jsonl_path: str):
        """
        Uploads a .jsonl file (batch) to OpenAI for use with the batch API.

        Args:
            jsonl_path (str): path to the .jsonl file containing
            batch requests.

        Returns:
            File: the uploaded file object.
        """
        with open(jsonl_path, "rb") as f:
            file_obj = await acreate_file(file=f, purpose="batch", custom_llm_provider="openai")
        logger.info(f"Batch uploaded to OpenAI: {file_obj.id}")
        return file_obj

    @staticmethod
    async def create_batch_job(file_id: str):
        """
        Creates a new batch job in OpenAI using the ID of the uploaded file.

        Args:
            file_id (str): The ID of the uploaded .jsonl file containing
            the batch requests.

        Returns:
            Batch: The created OpenAI batch job object.
        """
        batch = await acreate_batch(
            completion_window="24h",
            endpoint="/v1/chat/completions",
            input_file_id=file_id,
            custom_llm_provider="openai",
            litellm_logging=False,
        )
        logger.info(f"Batch work created: {batch.id}")
        return batch

    @staticmethod
    async def wait_for_batch_completion(batch_id: str) -> bool:
        """
        Checks the status of a batch job until it
        finalizes (with error or not).

        Args:
            batch_id (str): The ID of the batch job to monitor.

        Returns:
            bool: True if the batch was completed successfully,
            False otherwise.
        """
        while True:
            current = await aretrieve_batch(batch_id=batch_id, custom_llm_provider="openai")
            logger.info(f"Batch status: {current.status}")
            if current.status in ("completed", "failed", "expired", "cancelled") and current.output_file_id:
                break
            await asyncio.sleep(10)
        return current.status == "completed"

    @staticmethod
    async def retrieve_batch_output(batch_id: str) -> List[dict]:
        """
        Retrieves the results of a completed batch job from OpenAI.

        Args:
            batch_id (str): The ID of the completed batch job.

        Returns:
            List[dict]: A list of parsed JSON lines representing the responses
            from the batch job.
        """
        current = await aretrieve_batch(batch_id=batch_id, custom_llm_provider="openai")
        batch_output = await afile_content(file_id=current.output_file_id, custom_llm_provider="openai")
        lines = batch_output.text.strip().splitlines()

        return lines

    @staticmethod
    async def run_batch_api(jsonl_path: str):
        """
        Executes the complete lifecycle of a batch request to OpenAI

        Args:
            jsonl_path (str): Path to the JSONL file containing the
            batch prompts.

        Returns:
            List[dict] | None: The list of response objects if successful,
            or None if an error occurred.
        """
        try:
            file = await LLMClient.upload_batch_file(jsonl_path)
            batch = await LLMClient.create_batch_job(file.id)
            completed = await LLMClient.wait_for_batch_completion(batch.id)

            if not completed:
                logger.error(f"The batch was not completed: {batch.id}")
                return None

            batch_output = await LLMClient.retrieve_batch_output(batch.id)
            return batch_output

        except Exception as e:
            logger.error(f"Error during batch process: {e}")
            return None
