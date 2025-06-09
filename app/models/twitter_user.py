from pydantic import BaseModel, ConfigDict, Field


class TwitterUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    def __str__(self):
        return f"@{self.user_name} ({self.name})"

    id: str
    name: str
    user_name: str = Field(alias="userName")
