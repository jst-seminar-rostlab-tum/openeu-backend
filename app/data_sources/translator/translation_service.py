import json
import logging

from langdetect import detect

from app.services.llm_service.llm_client import LLMClient, LLMModels

logger = logging.getLogger(__name__)
base_prompt = (
    "You are a professional translator. Translate "
    "the following text to {target_lang}, "
    "without adding or removing meaning. Do not "
    "assume facts not present in the original "
    "text. Keep the translation as neutral and "
    "faithful as possible.\n\n{content}"
)


class ArticleTranslationService:
    @staticmethod
    def prepare_translation_batch(ids: list[str], texts: list[str]) -> tuple[list[str], list[str], list[dict]]:
        """
        Prepares prompts and auto-responses for a translation batch.

        Args:
            ids (list[str]): unique identifiers for each text.
            texts (list[str]): list of raw texts to translate.

        Returns:
            tuple: A tuple containing:
            - custom_ids (list[str]): IDs for requests that require
              translation.
            - prompts (list[str]): Prompts to send to the LLM.
            - auto_responses (list[dict]): Pre-filled responses for texts
              already in the target language.
        """
        if len(ids) != len(texts):
            logger.error("ids and texts must have the same length")
            return [], [], []

        target_langs = {"en": "English", "de": "German"}
        custom_ids, prompts, auto_responses = [], [], []

        for id_, text in zip(ids, texts):
            if not text or not text.strip():
                logger.warning(f"Empty text for id {id_}, skipping.")
                continue
            detected_lang = detect(text)

            for lang_code, lang_name in target_langs.items():
                full_id = f"{id_}_{lang_code}"
                if detected_lang == lang_code:
                    auto_responses.append(
                        {
                            "custom_id": full_id,
                            "response": {"body": {"choices": [{"message": {"content": text}}]}},
                        }
                    )
                else:
                    prompts.append(base_prompt.format(target_lang=lang_name, content=text))
                    custom_ids.append(full_id)

        return custom_ids, prompts, auto_responses

    @staticmethod
    async def execute_translation_batch(
        custom_ids: list[str], prompts: list[str], auto_responses: list[dict]
    ) -> list[dict]:
        """
        Executes the LLM batch translation process and combines results.

        Args:
            custom_ids (list[str]): identifiers for the translation requests.
            prompts (list[str]): prompts to send to the model.
            auto_responses (list[dict]): responses for texts already in the
            target language.

        Returns:
            list[dict]: All responses, including LLM completions
            and auto-responses.
        """
        batch_responses = []

        output_path = LLMClient.generate_batch(
            custom_ids=custom_ids,
            prompts=prompts,
            model=LLMModels.openai_4o.value,
            temperature=0.1,
            output_filename="openai_batch_translation.jsonl",
        )
        raw_lines = await LLMClient.run_batch_api(str(output_path))

        if raw_lines:
            batch_responses = [json.loads(line) for line in raw_lines]

        return batch_responses + auto_responses

    @staticmethod
    async def translate_all_fields(articles):
        """
        Prepares and translates all fields (title, content, summary)
        from a list of articles.

        Args:
            articles (list[Article]): List of article objects to be translated.

        Returns:
            list[dict]: List of translation responses.
        """
        all_ids = []
        all_texts = []

        all_ids.extend([f"{a.id}_title" for a in articles])
        all_texts.extend([a.title for a in articles])

        all_ids.extend([f"{a.id}_content" for a in articles])
        all_texts.extend([a.content for a in articles])

        all_ids.extend([f"{a.id}_summary" for a in articles])
        all_texts.extend([a.summary for a in articles])

        custom_ids, prompts, auto_responses = ArticleTranslationService.prepare_translation_batch(all_ids, all_texts)
        responses = await ArticleTranslationService.execute_translation_batch(custom_ids, prompts, auto_responses)

        return responses
