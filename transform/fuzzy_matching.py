"""A file to perform fuzzy matching."""

import pandas as pd
from rapidfuzz import process, fuzz


# def load_video_game_data():
#     """Loads video game data from CSV files."""

#     wcd_data = pd.read_csv("clean_woke_content_detector.csv")
#     vg_sales_data = pd.read_csv("videogame_sales.csv")
#     rawg_data = pd.read_csv("clean_rawg_video_games.csv")

#     return wcd_data, vg_sales_data, rawg_data

def load_video_game_data():
    """Loads video game data from CSV files."""
    try:
        wcd_data = pd.read_csv("clean_woke_content_detector.csv")
        vg_sales_data = pd.read_csv("videogame_sales.csv")
        rawg_data = pd.read_csv("clean_rawg_video_games.csv")
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
        raise
    return wcd_data, vg_sales_data, rawg_data

# def fuzzy_match(source_name: str, target_names: list[str], limit=1):
#     """Finds the best fuzzy match for a source name from a list of target names."""

#     matches = process.extract(
#         source_name, target_names, scorer=fuzz.ratio, limit=limit)
#     best_match, score = matches[0][:2] if matches else (None, 0)

#     return best_match, score


def fuzzy_match(source_name: str, target_names: list[str], limit=1, min_score=60) -> tuple:
    """Finds the best fuzzy match for a source name from a list of target names."""
    matches = process.extract(
        source_name, target_names, scorer=fuzz.ratio, limit=limit)
    best_match, score = matches[0][:2] if matches else (None, 0)

    if score < min_score:
        return None, 0

    return best_match, score


def match_row(row, vg_sales_data, rawg_data, match_threshold=80) -> pd.Series:
    """Fuzzy match a WCD row to video game sales and RAWG data."""

    game_name = row["Game"]

    # vg_best_match, vg_match_score = fuzzy_match(
    #     game_name, vg_sales_data["Name"].tolist())
    # vg_match_row = vg_sales_data[vg_sales_data["Name"] ==
    #                              vg_best_match].iloc[0] if vg_match_score >= match_threshold else {}

    # rawg_best_match, rawg_match_score = fuzzy_match(
    #     game_name, rawg_data["Name"].tolist())
    # rawg_match_row = rawg_data[rawg_data["Name"] ==
    #                            rawg_best_match].iloc[0] if rawg_match_score >= match_threshold else {}

    vg_best_match, vg_match_score = fuzzy_match(
        game_name, vg_sales_data["Name"].tolist())
    vg_matches = vg_sales_data[vg_sales_data["Name"] == vg_best_match]
    vg_match_row = vg_matches.iloc[0].to_dict(
    ) if vg_match_score >= match_threshold and not vg_matches.empty else {}

    rawg_best_match, rawg_match_score = fuzzy_match(
        game_name, rawg_data["Name"].tolist())
    rawg_matches = rawg_data[rawg_data["Name"] == rawg_best_match]
    rawg_match_row = rawg_matches.iloc[0].to_dict(
    ) if rawg_match_score >= match_threshold and not rawg_matches.empty else {}

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
    wcd_data, vg_sales_data, rawg_data = load_video_game_data()
    combined_df = wcd_data.apply(
        match_row, axis=1, args=(vg_sales_data, rawg_data))
    combined_df.to_csv(output_file, index=False)
    return combined_df


if __name__ == "__main__":

    process_video_game_data()
    # wcd_data, vg_sales_data, rawg_data = load_video_game_data()
    # combined_df = wcd_data.apply(
    #     match_row, axis=1, args=(vg_sales_data, rawg_data))
    # combined_df.to_csv("combined_video_game_data.csv", index=False)
