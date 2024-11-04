"A file to extract games data from the RAWG API."

from os import environ as ENV
import random
import logging
import requests
from requests.exceptions import RequestException

import pandas as pd
from dotenv import load_dotenv

from logging_config import logger_setup


LOGGER = logging.getLogger(__name__)


def fetch_sampled_games(api_key: str, page_size: int = 100, max_pages: int = 50):
    """Fetch a random sample of games from the RAWG API."""

    url = "https://api.rawg.io/api/games"
    all_games = []

    pages_to_fetch = random.sample(
        range(1, max_pages + 1), k=min(max_pages, 10))
    LOGGER.info("Fetching pages: %s", pages_to_fetch)

    for page in pages_to_fetch:
        LOGGER.info("Fetching page %s...", page)
        params = {
            "key": api_key,
            "page_size": page_size,
            "page": page,
            "ordering": "-rating"
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                results = response.json().get("results", [])

                if not results:
                    LOGGER.info("No more games found.")
                    break

                for game in results:
                    all_games.append({
                        "Name": game.get("name"),
                        "Rating": game.get("rating")
                    })
                LOGGER.info("Fetched %s games from page %s",
                            len(results), page)
            else:
                LOGGER.warning(
                    "Failed to fetch page %s (Status Code: %s)", page, response.status_code)

        except RequestException as req_err:
            LOGGER.error("Request error occurred: %s", req_err)
            break
        except Exception as err:
            LOGGER.error("An unexpected error occured: %s", err)
            break

    return all_games


def save_to_csv(games_data, filename='rawg_video_games.csv'):
    """Save game data to a CSV file."""

    df = pd.DataFrame(games_data)
    df.to_csv(filename, index=False)
    LOGGER.info("Data saved to %s", filename)


if __name__ == "__main__":

    logger_setup("rawg_api_extract_log.log", "logs")
    load_dotenv()
    LOGGER.info("Loading environment variables from .env file.")

    API_KEY = ENV["RAWG_KEY"]

    sampled_rawg_games = fetch_sampled_games(API_KEY)
    save_to_csv(sampled_rawg_games)
