import sys
import os
import unittest
from unittest.mock import patch
from app.data_sources.scraper_base import ScraperBase
from app.data_sources.scraper_base import ScraperResult

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestScraper(ScraperBase):
    def scrape_once(self, last_entry, **args):
        # Mock implementation for testing
        return ScraperResult(success=False, error=Exception("Test error"))


class TestScraperBase(unittest.TestCase):
    def test_notify_job_failure_called_on_scrape_failure(self):
        # Mock table name
        table_name = "test_table"

        # Create a TestScraper instance
        scraper = TestScraper(table_name=table_name)

        # Spy on notify_job_failure
        with patch("app.core.mail.notify_job_failure") as mock_notify_job_failure:
            # Run the scrape method
            scraper.scrape()

            # Assert notify_job_failure was called
            mock_notify_job_failure.assert_called_once_with(Exception, mock_notify_job_failure.call_args[0][1])


if __name__ == "__main__":
    unittest.main()
