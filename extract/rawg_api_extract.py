"A file to extract games data from the RAWG API."

from os import environ as ENV
import random
import logging
import requests

import pandas as pd
from dotenv import load_dotenv

from logging_config import logger_setup


LOGGER = logging.getLogger(__name__)


def fetch_sampled_games(api_key: str, max_pages: int = 50):
    """Fetch a random sample of games from the RAWG API."""

    url = "https://api.rawg.io/api/games"
    all_games = []

    ordering_options = [None, "rating", "-rating", "-released", "released"]
    random.shuffle(ordering_options)

    pages_to_fetch = random.sample(
        range(1, max_pages + 1), k=min(max_pages, 10))
    LOGGER.info("Fetching pages: %s", pages_to_fetch)

    for page in pages_to_fetch:
        ordering = random.choice(ordering_options)
        LOGGER.info("Fetching page %s...", page)
        params = {
            "key": api_key,
            "page_size": 40,
            "page": page
        }
        if ordering:
            params["ordering"] = ordering

        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            LOGGER.warning(
                "Failed to fetch page %s (Status Code: %s)", page, response.status_code)
            continue

        results = response.json().get("results", [])
        if not results:
            LOGGER.info("No more games found.")
            break

        for game in results:
            release_year = game.get("released", None)
            rawg_rating = game.get("rating", 0.0)
            metacritic_rating = game.get("metacritic", None)

            if (release_year and release_year != "N/A" and
                rawg_rating > 0.0 and
                    (metacritic_rating is not None and metacritic_rating > 0)):

                all_games.append({
                    "Name": game.get("name"),
                    "Rating": rawg_rating,
                    "Release Year": release_year,
                    "Metacritic": metacritic_rating
                })
            else:
                LOGGER.info("Excluding game: %s (Release Year: %s, RAWG Rating: %s, Metacritic: %s)",
                            game.get("name"), release_year, rawg_rating, metacritic_rating)

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
