"""A file to clean the video game data CSVs."""

import os
import logging
import pandas as pd

from utils.logging_config import logger_setup

LOGGER = logging.getLogger(__name__)


def load_data(csv_file: str) -> pd.DataFrame:
    """Loads data from specified CSV file."""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "extract", csv_file)

    if not os.path.exists(file_path):
        LOGGER.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        LOGGER.error("CSV file is empty: %s", csv_file)
        raise ValueError(f"CSV file is empty: {csv_file}")

    return df


def validate_column_count(df: pd.DataFrame, expected_column_count: int):
    """Checks if the DataFrame has the expected number of columns."""
    actual_column_count = len(df.columns)
    if actual_column_count < expected_column_count:
        LOGGER.error("Missing columns. Expected: %s, Found: %s",
                     expected_column_count, actual_column_count)
        raise ValueError("Missing columns. Expected: %s, Found: %s" %
                         (expected_column_count, actual_column_count))
    elif actual_column_count > expected_column_count:
        LOGGER.warning("Extra columns detected. Expected: %s, Found: %s",
                       expected_column_count, actual_column_count)


def clean_woke_content_detector_data() -> pd.DataFrame:
    """Cleans the Woke Content Detector data and saves it to a CSV."""
    expected_column_count = 6

    try:
        woke_data_csv = "woke_content_detector_full.csv"
        woke_data = load_data(woke_data_csv)

        validate_column_count(woke_data, expected_column_count)

        woke_data.columns = woke_data.columns.str.strip()
        woke_data = woke_data.rename(columns={
            "This list was put together by the Woke Content Detector Steam group with assistance from members of RPGHQ.": "Game",
            "👉": "Release Year",
            "Steam Group Link: https://steamcommunity.com/groups/Woke_Content_Detector": "Developer",
            "Curator Link: https://store.steampowered.com/curator/44927664-Woke-Content-Detector/": "Publisher",
            "👈": "Rating",
            "If you would like to support our work, please join our Steam group and follow our curator. Thank you!": "Review"
        })
        woke_data = woke_data.iloc[1:].reset_index(drop=True)

        # woke_data.columns = woke_data.iloc[0]
        # woke_data = woke_data.iloc[1:].reset_index(drop=True)

        woke_data = woke_data.replace("’", "'", regex=True)
        woke_data = woke_data.replace("–", "-", regex=True)
        woke_data = woke_data.replace("（", "(", regex=True)
        woke_data = woke_data.replace("）", ")", regex=True)

        woke_data = woke_data.drop_duplicates().reset_index(drop=True)

        woke_data.to_csv("clean_woke_content_detector.csv", index=True)
        LOGGER.info("Successfully cleaned and saved Woke Content Detector data")
        return woke_data
    except Exception as e:
        LOGGER.error("Error cleaning Woke Content Detector data: %s", str(e))
        return None


def clean_rawg_data() -> pd.DataFrame:
    """Cleans the data from the RAWG API and saves it to a CSV."""

    expected_column_count = 4
    try:
        rawg_data_csv = "rawg_video_games.csv"
        rawg_data = load_data(rawg_data_csv)

        validate_column_count(rawg_data, expected_column_count)

        rawg_data = rawg_data.replace("’", "'", regex=True)
        rawg_data = rawg_data.replace("–", "-", regex=True)
        rawg_data = rawg_data.drop_duplicates().reset_index(drop=True)

        rawg_data.to_csv("clean_rawg_video_games.csv", index=True)
        LOGGER.info("Successfully cleaned and saved RAWG data")
        return rawg_data
    except Exception as e:
        LOGGER.error("Error cleaning RAWG data: %s", str(e))
        return None


if __name__ == "__main__":
    logger_setup("clean_data_full_log.log", "logs")
    LOGGER.info("Starting data cleaning process.")

    clean_woke_content_detector_data()
    clean_rawg_data()

    LOGGER.info("Data cleaning process completed.")
