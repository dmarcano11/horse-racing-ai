"""Client for The Racing API."""
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta
import logging
from pathlib import Path
import json
import time

from src.config import settings
from src.models.meets import MeetsResponse
from src.utils.rate_limiter import RateLimiter
from src.models.entries import EntriesResponse
from src.models.results import ResultsResponse


logger = logging.getLogger(__name__)


class RacingAPIClient:
    """Client for interacting with The Racing API."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize API client.

        Args:
            username: API username (defaults to settings)
            password: API password (defaults to settings)
        """
        self.base_url = settings.racing_api_base_url
        self.auth = HTTPBasicAuth(
            username or settings.racing_api_username,
            password or settings.racing_api_password
        )
        self.rate_limiter = RateLimiter(
            max_requests=settings.rate_limit_requests,
            period=settings.rate_limit_period
        )
        self.session = requests.Session()
        self.session.auth = self.auth

        logger.info(f"Initialized Racing API client with base URL: {self.base_url}")

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make HTTP request with rate limiting, retry logic, and error handling.

        Args:
            endpoint: API endpoint (e.g., "/meets")
            params: Query parameters
            method: HTTP method
            max_retries: Maximum retry attempts for 429 errors

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            # Rate limit before each attempt
            self.rate_limiter.wait_if_needed()

            logger.debug(f"Attempt {attempt + 1}/{max_retries}: {method} {url} with params: {params}")

            try:
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=30
                )

                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        # Exponential backoff: 2, 4, 8 seconds
                        wait_time = 2 ** (attempt + 1)
                        logger.warning(
                            f"Rate limit hit (429). Waiting {wait_time}s before retry "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limit hit. Max retries exceeded.")
                        response.raise_for_status()

                # Raise for other HTTP errors
                response.raise_for_status()

                # Parse JSON
                data = response.json()

                logger.info(f"Successfully fetched data from {endpoint}")
                return data

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    # Continue to retry
                    continue
                logger.error(f"HTTP error occurred: {e}")
                logger.error(f"Response content: {e.response.text if e.response else 'N/A'}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error occurred: {e}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise

        # Should not reach here, but just in case
        raise requests.exceptions.HTTPError("Max retries exceeded")

    def get_meets(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        skip: int = 0
    ) -> MeetsResponse:
        """
        Fetch race meets for a date range.

        Args:
            start_date: Start date (defaults to today)
            end_date: End date (defaults to start_date)
            limit: Maximum results (1-50, default 50)
            skip: Pagination offset

        Returns:
            MeetsResponse with list of meets
        """
        # Default to today
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date

        # Validate limit
        limit = max(1, min(50, limit))

        # Build params
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "limit": limit,
            "skip": skip
        }

        # Make request
        data = self._make_request("/meets", params=params)

        # Parse and validate with Pydantic
        meets_response = MeetsResponse(**data)

        logger.info(
            f"Fetched {meets_response.total_meets} meets "
            f"from {start_date} to {end_date}"
        )

        return meets_response

    def save_meets_to_file(
            self,
            meets_response: MeetsResponse,
            filename: Optional[str] = None
    ) -> Path:
        """
        Save meets response to JSON file.

        Args:
            meets_response: MeetsResponse to save
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            # Generate filename with date range
            if meets_response.meets:
                first_date = meets_response.meets[0].date
                last_date = meets_response.meets[-1].date
                filename = f"meets_{first_date}_to_{last_date}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"meets_{timestamp}.json"

        # Save to raw data directory
        filepath = settings.raw_data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                meets_response.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False
            )

        logger.info(f"Saved meets data to {filepath}")
        return filepath

    def get_entries(self, meet_id: str) -> EntriesResponse:
        """
        Fetch race entries for a specific meet.

        Args:
            meet_id: Meet ID from meets endpoint

        Returns:
            EntriesResponse with all races and runners
        """
        logger.info(f"Fetching entries for meet: {meet_id}")

        # Make request
        endpoint = f"/meets/{meet_id}/entries"
        data = self._make_request(endpoint)

        # Parse and validate with Pydantic
        entries_response = EntriesResponse(**data)

        logger.info(
            f"Fetched {entries_response.total_races} races "
            f"with {entries_response.total_runners} total runners "
            f"for {entries_response.track_name}"
        )

        return entries_response

    def save_entries_to_file(
            self,
            entries_response: EntriesResponse,
            filename: Optional[str] = None
    ) -> Path:
        """
        Save entries response to JSON file.

        Args:
            entries_response: EntriesResponse to save
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            # Generate filename
            meet_id = entries_response.meet_id
            track_name = entries_response.track_name.replace(" ", "_")
            filename = f"entries_{meet_id}_{track_name}.json"

        # Save to raw data directory
        filepath = settings.raw_data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                entries_response.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False
            )

        logger.info(f"Saved entries data to {filepath}")
        return filepath

    def get_results(self, meet_id: str) -> ResultsResponse:
        """
        Fetch race results for a specific meet.

        Args:
            meet_id: Meet ID from meets endpoint

        Returns:
            ResultsResponse with all race results
        """
        logger.info(f"Fetching results for meet: {meet_id}")

        # Make request
        endpoint = f"/meets/{meet_id}/results"
        data = self._make_request(endpoint)

        # Parse and validate with Pydantic
        results_response = ResultsResponse(**data)

        logger.info(
            f"Fetched results for {results_response.total_races} races "
            f"({results_response.completed_races} completed) "
            f"for {results_response.track_name}"
        )

        return results_response

    def save_results_to_file(
            self,
            results_response: ResultsResponse,
            filename: Optional[str] = None
    ) -> Path:
        """
        Save results response to JSON file.

        Args:
            results_response: ResultsResponse to save
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            # Generate filename
            meet_id = results_response.meet_id
            track_name = results_response.track_name.replace(" ", "_")
            filename = f"results_{meet_id}_{track_name}.json"

        # Save to raw data directory
        filepath = settings.raw_data_dir / filename

        # Use model_dump with mode='json' to handle Decimal serialization
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                results_response.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False
            )

        logger.info(f"Saved results data to {filepath}")
        return filepath

    def close(self):
        """Close the session."""
        self.session.close()
        logger.info("Closed Racing API client session")