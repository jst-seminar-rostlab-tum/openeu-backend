import logging
from datetime import datetime, timedelta
from datetime import timezone as tz

import requests

from app.core.config import Settings
from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.models.tweet import Tweet
from app.models.twitter_user import TwitterUser

TWEETS_TABLE_NAME = "tweets"
SCRAPE_LOOKBACK_DAYS = 1

logger = logging.getLogger(__name__)


class TweetScraper(ScraperBase):
    """
    A class to scrape tweets from a specific Twitter user since a specified date.
    """

    def __init__(self, usernames: list[str]):
        super().__init__(TWEETS_TABLE_NAME)
        settings = Settings()
        self.base_url = "https://api.twitterapi.io"
        self.headers = {"X-API-Key": settings.get_twitter_api_key()}
        self.max_recursion_depth = 10
        self.usernames = usernames

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
        for tweet in tweets:
            tweet.embedding_input = str(tweet)

        # Check if the last tweet is older than the specified date
        if tweets and tweets[-1].created_at < since:
            return tweets

        # If a next cursor is available, recursively fetch more tweets and append them
        has_next_page = tweets_response_json["has_next_page"]
        next_cursor = tweets_response_json["next_cursor"]
        if has_next_page and next_cursor:
            try:
                next_tweets = self._get_user_tweets_since_rec(user_id, since, next_cursor, recursion_depth + 1)
                tweets.extend(next_tweets)
                return tweets
            except Exception as e:
                logger.error(f"Error fetching next page of tweets, returning what we have so far: {e}")
                return tweets
        else:
            return tweets

    def _get_user_tweets_since(self, username: str, since: datetime) -> list[Tweet]:
        user = self._get_user(username)
        tweets = self._get_user_tweets_since_rec(user_id=user.id, since=since, cursor="", recursion_depth=0)
        return [tweet for tweet in tweets if tweet.created_at >= since]

    def _scrape_all_usernames(self):
        since = datetime.now(tz.utc) - timedelta(days=SCRAPE_LOOKBACK_DAYS)

        for username in self.usernames:
            tweets = self._get_user_tweets_since(username, since)
            for tweet in tweets:
                error_result = self.store_entry(tweet.model_dump(mode="json"), embedd_entries=True)
                if error_result:
                    return error_result
                self.last_entry = tweet

    def scrape_once(self, last_entry, **args) -> ScraperResult:
        logger.info(f"Starting tweet scraping for {len(self.usernames)} usernames...")
        try:
            self._scrape_all_usernames()
        except Exception as e:
            logger.error(f"Error during tweet scraping: {e}")
            return ScraperResult(False, error=e)
        logger.info("Tweet scraping completed successfully.")
        return ScraperResult(True)
