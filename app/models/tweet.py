from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.twitter_user import TwitterUser


class BaseTweet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    text: str
    author: TwitterUser

    embedding_input: Optional[str] = None

    created_at: datetime = Field(alias="createdAt")

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_custom_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%a %b %d %H:%M:%S %z %Y")
        return v

    reply_count: int = Field(alias="replyCount")
    view_count: int = Field(alias="viewCount")
    like_count: int = Field(alias="likeCount")
    quote_count: int = Field(alias="quoteCount")


class SimpleTweet(BaseTweet):
    pass


class Tweet(BaseTweet):
    def __str__(self):
        result = f"On {self.created_at.strftime('%d.%m.%Y')} at {self.created_at.strftime('%H:%M')} UTC, {self.author} "
        if self.quoted_tweet:
            result += f'quoted {self.quoted_tweet.author}, commenting:\n"{self.text}"'
            result += f'\n\nQuoted tweet: "{self.quoted_tweet.text}"'
        elif self.retweeted_tweet:
            result += f"retweeted {self.retweeted_tweet.author}:\n"
            result += f'"{self.retweeted_tweet.text}"'
        else:
            result += f'tweeted:\n"{self.text}"'

        return result

    quoted_tweet: Optional[SimpleTweet] = None
    retweeted_tweet: Optional[SimpleTweet] = None
