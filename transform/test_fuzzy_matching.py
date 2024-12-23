"""Tests functions for fuzzy_matching.py."""
# pylint: skip-file
import pytest
import pandas as pd
from unittest.mock import patch
from fuzzy_matching import (load_video_game_data, fuzzy_match, match_row,
                            get_matched_row, process_video_game_data)


@patch("fuzzy_matching.LOGGER.info")
@patch("pandas.read_csv")
def test_load_video_game_data_valid(mock_read_csv, mock_logging):
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
    mock_logging.assert_called_with("Successfully loaded all data files")


@patch("fuzzy_matching.LOGGER.error")
@patch("pandas.read_csv")
def test_load_video_game_data_file_missing(mock_read_csv, mock_logging):
    """Test load_video_game_data handles missing files properly."""
    error = FileNotFoundError("File not found.")
    mock_read_csv.side_effect = error

    with pytest.raises(FileNotFoundError):
        load_video_game_data()

    mock_logging.assert_called_with("File not found: %s", error)


def test_fuzzy_match_valid():
    """Test the match returns with score of over 80 successful."""

    source_name = "Assassin's Creed"
    target_names = ["Assassin Creed", "Battlefield", "Call of Duty"]

    best_match, score = fuzzy_match(source_name, target_names)

    assert best_match == "Assassin Creed"
    assert score > 80


@patch("fuzzy_matching.LOGGER.warning")
def test_fuzzy_match_no_valid_matches(mock_logging):
    """Test that no valid match raises warning message."""
    source_name = "Game1"
    target_names = ["Assassin Creed", "Battlefield"]
    best_match, score = fuzzy_match(
        source_name, target_names, limit=1, min_score=80)
    assert best_match is None
    assert score == 0

    mock_logging.assert_called_with(
        "No match found above threshold for: %s (score: %s)", source_name, 25.0)


def test_get_matched_row_valid_match():
    """Test get_matched_row returns correct data for valid match."""
    df = pd.DataFrame({
        "Name": ["Game1"],
        "Value": [100]
    })
    result = get_matched_row("Game1", df, 80)
    assert result["Value"] == 100


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


@patch("fuzzy_matching.LOGGER.info")
def test_match_row_logs_processing(mock_logging):
    """Test that game processing is logged successfully."""
    row = pd.Series({"Game": "TestGame"})
    df = pd.DataFrame({"Name": ["Game1"]})
    match_row(row, df, df)
    mock_logging.assert_called_with("Processing game: %s", "TestGame")


@patch("fuzzy_matching.LOGGER.info")
def test_process_video_game_data_logs_completion(mock_logging):
    """Test that process completion is logged."""
    with patch("fuzzy_matching.load_video_game_data") as mock_load:
        mock_load.return_value = (
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        process_video_game_data()
        mock_logging.assert_called_with("Saving combined data to %s",
                                        "combined_video_game_data.csv")


def test_match_row_no_matches():
    """Test match_row where no matches meet the threshold."""
    wcd_row = {
        "Game": "Unknown Game",
        "Release Year": "N/A",
        "Developer": "N/A",
        "Publisher": "N/A",
        "Rating": "N/A",
        "Review": "N/A"
    }
    vg_sales_data = pd.DataFrame({
        "Name": ["Assassin Creed", "Battlefield"],
        "Global_Sales": [3.2, 4.5]
    })
    rawg_data = pd.DataFrame({
        "Name": ["Assassin Creed", "Call of Duty"],
        "RAWG Rating": [88, 90]
    })
    result = match_row(pd.Series(wcd_row),
                       vg_sales_data,
                       rawg_data,
                       match_threshold=90
                       )
    expected_result = pd.Series({
        "Name": "Unknown Game",
        "Release Year": "N/A",
        "Developer": "N/A",
        "Publisher": "N/A",
        "WCD Rating": "N/A",
        "WCD Review": "N/A",
        "RAWG Rating": None,
        "Metacritic Rating": None,
        "North American Sales": None,
        "European Sales": None,
        "Japanese Sales": None,
        "Other Sales": None,
        "Global Sales": None,
    })
    pd.testing.assert_series_equal(result, expected_result)


def test_match_row_valid_near_threshold():
    """Test match_row when match is just at the threshold."""
    wcd_row = {"Game": "Assassin Creed"}

    vg_sales_data = pd.DataFrame({
        "Name": ["Assassin's Creed"],
        "NA_Sales": [1.5],
    })

    rawg_data = pd.DataFrame({
        "Name": ["Call of Duty"],
        "RAWG Rating": [95]
    })

    result = match_row(pd.Series(wcd_row), vg_sales_data,
                       rawg_data, match_threshold=80)

    assert result["Name"] == "Assassin Creed"
    assert result["North American Sales"] == 1.5


@patch("pandas.DataFrame.to_csv")
@patch("fuzzy_matching.load_video_game_data")
def test_main_workflow(mock_load_video_game_data, mock_to_csv):
    """Test that the main workflow runs successfully."""
    mock_wcd_data = pd.DataFrame({
        "Game": ["Game1"],
        "Release Year": ["2023"],
        "Developer": ["Dev1"],
        "Publisher": ["Pub1"],
        "Rating": ["Recommended"],
        "Review": ["Great game."]
    })
    mock_vg_sales_data = pd.DataFrame({
        "Name": ["Game1"],
        "NA_Sales": [1.0],
        "EU_Sales": [2.0],
        "JP_Sales": [0.5],
        "Other_Sales": [1.0],
        "Global_Sales": [4.5]
    })
    mock_rawg_data = pd.DataFrame({
        "Name": ["Game1"],
        "RAWG Rating": [90],
        "Metacritic Rating": [85]
    })

    mock_load_video_game_data.return_value = (
        mock_wcd_data, mock_vg_sales_data, mock_rawg_data
    )

    wcd_data, vg_sales_data, rawg_data = mock_load_video_game_data()
    combined_df = wcd_data.apply(
        match_row, axis=1, args=(vg_sales_data, rawg_data))
    combined_df.to_csv("combined_video_game_data.csv", index=False)

    mock_to_csv.assert_called_once_with(
        "combined_video_game_data.csv", index=False)
