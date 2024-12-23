"""Tests functions for clean_csvs.py."""
# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
import os
import pandas as pd
from clean_csvs import (load_data,
                        clean_woke_content_detector_data,
                        clean_rawg_data, validate_column_count)


@patch("clean_csvs.os.path.exists")
@patch("clean_csvs.os.path.join")
@patch("clean_csvs.os.path.dirname")
@patch("clean_csvs.pd.read_csv")
def test_load_woke_data_valid(mock_read_csv, mock_dirname, mock_join, mock_exists):
    """Tests woke data loaded successfully."""
    mock_woke_df = pd.DataFrame({
        "Game": ["Bloons TD 6", "Starfield"],
        "Review": ["Contains overtly pro-LGBTQ+ messaging.", "Contains subtly pro-DEI messaging."]
    })

    mock_dirname.return_value = "/fake/path"
    mock_join.return_value = "/fake/path/woke_content_detector_full.csv"
    mock_read_csv.return_value = mock_woke_df
    mock_exists.return_value = True

    result = load_data("woke_content_detector_full.csv")

    mock_dirname.assert_called_once()
    mock_join.assert_called_once_with(
        "/fake/path", "..", "extract", "woke_content_detector_full.csv")
    mock_read_csv.assert_called_once_with(
        "/fake/path/woke_content_detector_full.csv")
    assert all(col in result.columns for col in ["Game", "Review"])
    assert "Game", "Review" in result
    assert "Bloons TD 6", "Starfield" in result


@patch("clean_csvs.os.path.exists")
@patch("clean_csvs.os.path.join")
@patch("clean_csvs.os.path.dirname")
@patch("clean_csvs.pd.read_csv")
def test_load_rawg_data_valid(mock_read_csv, mock_dirname, mock_join, mock_exists):
    """Tests rawg data is loaded successfully."""
    mock_rawg_df = pd.DataFrame({
        "Name": ["VVVVVV", "Bug Princess"],
        "Release Year": ["2016", "2020"]
    })

    mock_dirname.return_value = "/fake/path"
    mock_join.return_value = "/fake/path/rawg_video_games.csv"
    mock_read_csv.return_value = mock_rawg_df
    mock_exists.return_value = True

    result = load_data("rawg_video_games.csv")

    mock_dirname.assert_called_once()
    mock_join.assert_called_once_with(
        "/fake/path", "..", "extract", "rawg_video_games.csv")
    mock_read_csv.assert_called_once_with(
        "/fake/path/rawg_video_games.csv")
    assert all(col in result.columns for col in ["Name", "Release Year"])
    assert "Name", "Release Year" in result
    assert "VVVVV", "2016" in result


@patch("clean_csvs.LOGGER.error")
@patch("clean_csvs.os.path.exists")
@patch("clean_csvs.os.path.join")
@patch("clean_csvs.os.path.dirname")
def test_load_data_file_not_found(mock_dirname, mock_join, mock_exists, mock_logging):
    """Tests that FileNotFoundError is raised when file doesn't exist."""
    mock_dirname.return_value = "/fake/path"
    mock_join.return_value = "/fake/path/nonexistent.csv"
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError):
        load_data("nonexistent.csv")

    mock_logging.assert_called_with(
        "File not found: %s", "/fake/path/nonexistent.csv")


@patch("clean_csvs.LOGGER.error")
@patch("clean_csvs.os.path.exists")
@patch("clean_csvs.os.path.join")
@patch("clean_csvs.os.path.dirname")
@patch("clean_csvs.pd.read_csv")
def test_load_data_empty_csv(mock_read_csv, mock_dirname, mock_join, mock_exists, mock_logging):
    """Tests that ValueError is raised when CSV is empty."""
    mock_dirname.return_value = "/fake/path"
    mock_join.return_value = "/fake/path/empty.csv"
    mock_exists.return_value = True
    mock_read_csv.return_value = pd.DataFrame()

    with pytest.raises(ValueError):
        load_data("empty.csv")

    mock_logging.assert_called_with("CSV file is empty: %s", "empty.csv")

##


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.load_data")
def test_clean_woke_content_detector_column_renaming_valid(mock_load_data, mock_to_csv):
    """Tests columns are renamed correctly."""
    test_df = pd.DataFrame({
        "This list was put together by the Woke Content Detector Steam group with assistance from members of RPGHQ.": ["Game1"],
        "👉": ["2023"],
        "Steam Group Link: https://steamcommunity.com/groups/Woke_Content_Detector": ["Dev1"],
        "Curator Link: https://store.steampowered.com/curator/44927664-Woke-Content-Detector/": ["Pub1"],
        "👈": ["Rating1"],
        "If you would like to support our work, please join our Steam group and follow our curator. Thank you!": ["Review1"]
    })

    mock_load_data.return_value = test_df

    result = clean_woke_content_detector_data()

    mock_to_csv.assert_called_once_with(
        "clean_woke_content_detector.csv", index=True)
    expected_columns = ["Game", "Release Year",
                        "Developer", "Publisher", "Rating", "Review"]
    assert all(col in result.columns for col in expected_columns)


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.load_data")
def test_clean_woke_content_detector_special_characters_valid(mock_load_data, mock_to_csv):
    """Tests special characters are correctly cleaned."""
    test_df = pd.DataFrame({
        "Game": ["Assassin's Creed (Remastered) III", "Starfield"],
        "Release Year": ["2023", "2020"],
        "Developer": ["Ninja–Kiwi", "Nintendo"],
        "Publisher": ["Ninja–Kiwi.", "Nintendo "],
        "Rating": ["Not Recommended", "Not Recommended"],
        "Review": ["Contains overtly pro-LGBTQ+ messaging.", "Contains subtly pro-DEI messaging."]
    })

    mock_load_data.return_value = test_df
    result = clean_woke_content_detector_data()

    mock_to_csv.assert_called_once_with(
        "clean_woke_content_detector.csv", index=True)
    expected_df = pd.DataFrame({
        "Game": ["Assassin's Creed(Remastered)III", "Starfield"],
        "Release Year": ["2023", "2020"],
        "Developer": ["Ninja-Kiwi", "Nintendo"],
        "Publisher": ["Ninja-Kiwi.", "Nintendo "],
        "Rating": ["Not Recommended", "Not Recommended"],
        "Review": ["Contains overtly pro-LGBTQ+ messaging.", "Contains subtly pro-DEI messaging."]
    }).iloc[1:].reset_index(drop=True)

    pd.testing.assert_frame_equal(result, expected_df)

####


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.LOGGER.error")
@patch("clean_csvs.load_data")
def test_clean_woke_content_detector_exception_handling(mock_load_data, mock_logging, mock_to_csv):
    """Tests exception handling in clean_woke_content_detector_data function."""
    mock_load_data.side_effect = Exception("Error")

    result = clean_woke_content_detector_data()

    assert result is None
    mock_logging.assert_called_with(
        "Error cleaning Woke Content Detector data: %s", "Error")
    mock_to_csv.assert_not_called()


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.load_data")
def test_clean_woke_content_detector_duplicate_removal(mock_load_data, mock_to_csv):
    """Tests that duplicates are removed successfully from woke content detector data."""
    test_df = pd.DataFrame({
        "Game": ["Game1", "Game1", "Game2"],
        "Release Year": ["2023", "2023", "2020"],
        "Developer": ["Dev1", "Dev1", "Dev2"],
        "Publisher": ["Pub1", "Pub1", "Pub2"],
        "Rating": ["R1", "R1", "R2"],
        "Review": ["Rev1", "Rev1", "Rev2"]
    })

    mock_load_data.return_value = test_df

    result = clean_woke_content_detector_data()

    assert len(result) == 2
    assert list(result["Game"]) == ["Game1", "Game2"]
    mock_to_csv.assert_called_once_with(
        "clean_woke_content_detector.csv", index=True)


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.load_data")
def test_clean_rawg_data_special_characters_valid(mock_load_data, mock_to_csv):
    """Tests that special characters in RAWG data are cleaned correctly."""

    test_df = pd.DataFrame({
        "Name": ["Assassin’s Creed III", "Star–Field"],
        "Release Year": ["2023", "2020"],
        "RAWG Rating": ["3.51", "2.90"],
        "Metacritic Rating": ["78.0", "71.0"]
    })

    mock_load_data.return_value = test_df

    result = clean_rawg_data()

    mock_to_csv.assert_called_once_with(
        "clean_rawg_video_games.csv", index=True)

    expected_df = pd.DataFrame({
        "Name": ["Assassin's Creed III", "Star-Field"],
        "Release Year": ["2023", "2020"],
        "RAWG Rating": ["3.51", "2.90"],
        "Metacritic Rating": ["78.0", "71.0"]
    })

    pd.testing.assert_frame_equal(result, expected_df)


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.LOGGER.error")
@patch("clean_csvs.load_data")
def test_clean_rawg_data_exception_handling(mock_load_data, mock_logging, mock_to_csv):
    """Tests exception handling in clean_rawg_data function."""
    mock_load_data.side_effect = Exception("Error")

    result = clean_rawg_data()

    assert result is None
    mock_logging.assert_called_with(
        "Error cleaning RAWG data: %s", "Error")
    mock_to_csv.assert_not_called()


@patch("pandas.DataFrame.to_csv")
@patch("clean_csvs.load_data")
def test_clean_rawg_data_duplicate_removal(mock_load_data, mock_to_csv):
    """Tests that duplicates are removed successfully from RAWG data."""
    test_df = pd.DataFrame({
        "Name": ["Game1", "Game1", "Game2"],
        "Release Year": ["2023", "2023", "2020"],
        "RAWG Rating": [3.51, 3.51, 2.5],
        "Metacritic Rating": [78.0, 78.0, 79.0]
    })

    mock_load_data.return_value = test_df

    result = clean_rawg_data()

    assert len(result) == 2
    assert list(result["Name"]) == ["Game1", "Game2"]

    mock_to_csv.assert_called_once_with(
        "clean_rawg_video_games.csv", index=True)

##


@patch("clean_csvs.LOGGER.error")
def test_validate_column_count_correct_columns(mock_logging):
    """Tests that no error is raised for correct column count."""
    df = pd.DataFrame({"column1": [1], "column2": [2]})
    validate_column_count(df, 2)

    mock_logging.assert_not_called()


@patch("clean_csvs.LOGGER.error")
def test_validate_column_count_missing_columns(mock_logging):
    """Tests ValueError is raised for missing columns."""
    df = pd.DataFrame({"column1": [1], "column2": [2]})

    with pytest.raises(ValueError):
        validate_column_count(df, 3)

    mock_logging.assert_called_with(
        "Missing columns. Expected: %s, Found: %s", 3, 2
    )


@patch("clean_csvs.LOGGER.warning")
def test_validate_column_count_extra_columns(mock_logging):
    """Tests a warning occurs for extra columns."""
    df = pd.DataFrame({"column1": [1], "column2": [
                      2], "column3": [3]})

    validate_column_count(df, 2)

    mock_logging.assert_called_with(
        "Extra columns detected. Expected: %s, Found: %s", 2, 3
    )
