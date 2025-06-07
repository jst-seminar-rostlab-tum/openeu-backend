from datetime import datetime

import requests

from app.core.config import Settings
from app.models.tweet import Tweet
from app.models.twitter_user import TwitterUser


class TweetScraper:
    """
    A class to scrape tweets from a specific Twitter user since a specified date.
    """

    def __init__(self):
        settings = Settings()
        self.base_url = "https://api.twitterapi.io"
        self.headers = {"X-API-Key": settings.get_twitter_api_key()}
        self.max_recursion_depth = 10

    def _get_user(self, username: str) -> TwitterUser:
        """
        Get the user ID for a given username.
        """
        response = requests.get(
            f"{self.base_url}/twitter/user/info",
            headers=self.headers,
            params={"userName": username},
        )
        response.raise_for_status()
        data = response.json()["data"]
        return TwitterUser(**data)

    def _get_user_tweets_since_rec(
        self, user_id: str, since: datetime, cursor: str, recursion_depth: int
    ) -> list[Tweet]:
        if recursion_depth > self.max_recursion_depth:
            raise Exception("Too many pages requested, stopping to prevent infinite loop")

        print("[REQUEST] Fetching tweets for user:", user_id, "with cursor:", cursor)

        tweets_response = requests.get(
            "https://api.twitterapi.io/twitter/user/last_tweets",
            headers=self.headers,
            params={"userId": user_id, "cursor": cursor},
        )
        tweets_response.raise_for_status()
        tweets_response_json = tweets_response.json()
        if tweets_response_json["code"] and tweets_response_json["code"] != 0:
            raise Exception(f"Error fetching tweets: {tweets_response_json['msg']}")

        if not tweets_response_json["data"] or not tweets_response_json["data"]["tweets"]:
            raise Exception("No data returned from the API")

        tweets_json = tweets_response_json["data"]["tweets"]
        tweets = [Tweet(**tweet) for tweet in tweets_json]

        # Check if the last tweet is older than the specified date
        if tweets and tweets[-1].created_at < since:
            return tweets

        # If a next cursor is available, recursively fetch more tweets and append them
        has_next_page = tweets_response_json["has_next_page"]
        next_cursor = tweets_response_json["next_cursor"]
        if has_next_page and next_cursor:
            next_tweets = self._get_user_tweets_since_rec(user_id, since, next_cursor, recursion_depth + 1)
            tweets.extend(next_tweets)
            return tweets
        else:
            return tweets

    def get_user_tweets_since(self, username: str, since: datetime) -> list[Tweet]:
        user = self._get_user(username)
        tweets = self._get_user_tweets_since_rec(user_id=user.id, since=since, cursor="", recursion_depth=0)
        return [tweet for tweet in tweets if tweet.created_at >= since]


tweet_scraper = TweetScraper()
