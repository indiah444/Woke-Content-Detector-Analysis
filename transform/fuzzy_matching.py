"""A file to perform fuzzy matching."""
import logging
import pandas as pd
from rapidfuzz import process, fuzz
from utils.logging_config import logger_setup

LOGGER = logging.getLogger(__name__)


def load_video_game_data() -> tuple:
    """Loads video game data from CSV files."""
    try:
        LOGGER.info("Loading video game data from CSV files")
        wcd_data = pd.read_csv("clean_woke_content_detector.csv")
        vg_sales_data = pd.read_csv("videogame_sales.csv")
        rawg_data = pd.read_csv("clean_rawg_video_games.csv")
        LOGGER.info("Successfully loaded all data files")
        return wcd_data, vg_sales_data, rawg_data
    except FileNotFoundError as e:
        LOGGER.error("File not found: %s", e)
        raise


def fuzzy_match(source_name: str, target_names: list[str], limit=1, min_score=80) -> tuple:
    """Finds the best fuzzy match for a source name from a list of target names."""
    matches = process.extract(
        source_name, target_names, scorer=fuzz.ratio, limit=limit)
    best_match, score = matches[0][:2] if matches else (None, 0)

    if score < min_score:
        LOGGER.warning(
            "No match found above threshold for: %s (score: %s)", source_name, score)
        return None, 0

    LOGGER.info("Match found for %s: %s (score: %s)",
                source_name, best_match, score)
    return best_match, score


def get_matched_row(game_name: str, df: pd.DataFrame, match_threshold: int) -> dict:
    """Get matching row from dataframe using fuzzy matching."""
    best_match, match_score = fuzzy_match(game_name, df["Name"].tolist())
    matches = df[df["Name"] == best_match]
    return matches.iloc[0].to_dict() if match_score >= match_threshold and not matches.empty else {}


def match_row(row, vg_sales_data, rawg_data, match_threshold=80) -> pd.Series:
    """Fuzzy match a WCD row to video game sales and RAWG data."""
    game_name = row["Game"]
    LOGGER.info("Processing game: %s", game_name)

    vg_match_row = get_matched_row(game_name, vg_sales_data, match_threshold)
    rawg_match_row = get_matched_row(game_name, rawg_data, match_threshold)

    return pd.Series({
        "Name": game_name,
        "Release Year": row.get("Release Year", "N/A"),
        "Developer": row.get("Developer", "N/A"),
        "Publisher": row.get("Publisher", "N/A"),
        "WCD Rating": row.get("Rating", "N/A"),
        "WCD Review": row.get("Review", "N/A"),
        "RAWG Rating": rawg_match_row.get("RAWG Rating", None),
        "Metacritic Rating": rawg_match_row.get("Metacritic Rating", None),
        "North American Sales": vg_match_row.get("NA_Sales", None),
        "European Sales": vg_match_row.get("EU_Sales", None),
        "Japanese Sales": vg_match_row.get("JP_Sales", None),
        "Other Sales": vg_match_row.get("Other_Sales", None),
        "Global Sales": vg_match_row.get("Global_Sales", None),
    })


def process_video_game_data(output_file: str = "combined_video_game_data.csv") -> pd.DataFrame:
    """Process and combine video game data from multiple sources."""
    LOGGER.info("Starting video game data processing")
    wcd_data, vg_sales_data, rawg_data = load_video_game_data()

    LOGGER.info("Matching and combining datasets")
    combined_df = wcd_data.apply(
        match_row, axis=1, args=(vg_sales_data, rawg_data))

    LOGGER.info("Saving combined data to %s", output_file)
    combined_df.to_csv(output_file, index=False)
    return combined_df


if __name__ == "__main__":
    logger_setup("fuzzy_matching_log.log", "logs")
    LOGGER.info("Starting fuzzy matching process")
    process_video_game_data()
    LOGGER.info("Fuzzy matching process completed")
