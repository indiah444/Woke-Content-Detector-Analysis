"""Tests functions for fuzzy_matching.py."""
# pylint: skip-file
import pandas as pd
from unittest.mock import patch
from fuzzy_matching import load_video_game_data, fuzzy_match, match_row


@patch("pandas.read_csv")
def test_load_video_game_data_valid(mock_read_csv):
    """Test that load_video_game_data correctly loads data from CSVs."""

    wcd_data_mock = pd.DataFrame(
        {"Game": ["Game1"], "Rating": ["Not Recommended"]})
    vg_sales_data_mock = pd.DataFrame(
        {"Name": ["Game1"], "Global_Sales": [1.0]})
    rawg_data_mock = pd.DataFrame({"Name": ["Game1"], "RAWG Rating": [90.0]})

    mock_read_csv.side_effect = [wcd_data_mock,
                                 vg_sales_data_mock, rawg_data_mock]

    wcd_data, vg_sales_data, rawg_data = load_video_game_data()

    pd.testing.assert_frame_equal(wcd_data, wcd_data_mock)
    pd.testing.assert_frame_equal(vg_sales_data, vg_sales_data_mock)
    pd.testing.assert_frame_equal(rawg_data, rawg_data_mock)


def test_fuzzy_match_valid():
    """Test the match returns with score of over 80 successful."""

    source_name = "Assassin's Creed"
    target_names = ["Assassin Creed", "Battlefield", "Call of Duty"]

    best_match, score = fuzzy_match(source_name, target_names)

    assert best_match == "Assassin Creed"
    assert score > 80


def test_match_row_valid():
    """Test the match_row function for correct matching."""
    wcd_row = {
        "Game": "Assassin's Creed",
        "Release Year": "2023",
        "Developer": "Ubisoft",
        "Publisher": "Ubisoft",
        "Rating": "Recommended",
        "Review": "Great game with good mechanics."
    }

    vg_sales_data = pd.DataFrame({
        "Name": ["Assassin Creed", "Battlefield"],
        "NA_Sales": [1.5, 2.0],
        "EU_Sales": [1.0, 1.5],
        "JP_Sales": [0.2, 0.3],
        "Other_Sales": [0.5, 0.7],
        "Global_Sales": [3.2, 4.5]
    })

    rawg_data = pd.DataFrame({
        "Name": ["Assassin Creed", "Call of Duty"],
        "RAWG Rating": [88, 95],
        "Metacritic Rating": [85, 90]
    })

    result = match_row(pd.Series(wcd_row), vg_sales_data, rawg_data)

    expected_result = pd.Series({
        "Name": "Assassin's Creed",
        "Release Year": "2023",
        "Developer": "Ubisoft",
        "Publisher": "Ubisoft",
        "WCD Rating": "Recommended",
        "WCD Review": "Great game with good mechanics.",
        "RAWG Rating": 88,
        "Metacritic Rating": 85,
        "North American Sales": 1.5,
        "European Sales": 1.0,
        "Japanese Sales": 0.2,
        "Other Sales": 0.5,
        "Global Sales": 3.2
    })

    pd.testing.assert_series_equal(result, expected_result)
