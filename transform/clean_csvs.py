"""A file to clean the video game data CSVs."""

import pandas as pd


def load_woke_data():
    """Loads the Woke Content Detector CSV."""

    return pd.read_csv("extract/woke_content_detector_full.csv")


def clean_woke_content_detector_data():
    """Cleans the Woke Content Detector data and saves it to a CSV."""

    woke_data = load_woke_data()

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

    woke_data = woke_data.replace("’", "'", regex=True)
    woke_data = woke_data.replace("–", "-", regex=True)
    woke_data = woke_data.replace("（", "(", regex=True)
    woke_data = woke_data.replace("）", ")", regex=True)

    return woke_data.to_csv("clean_woke_content_detector.csv")


def clean_rawg_data():
    """Cleans the data from the RAWG API and saves it to a CSV."""

    pass


if __name__ == "__main__":

    clean_woke_content_detector_data()
