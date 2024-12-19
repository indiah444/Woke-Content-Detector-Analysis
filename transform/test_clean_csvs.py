"""Tests functions for clean_csvs.py."""
# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
import os
import pandas as pd
from clean_csvs import (load_woke_data, load_rawg_data,
                        clean_woke_content_detector_data, clean_rawg_data)


@patch("clean_csvs.os.path.join")
@patch("clean_csvs.os.path.dirname")
@patch("clean_csvs.pd.read_csv")
def test_load_woke_data_valid(mock_read_csv, mock_dirname, mock_join):
    """Tests woke data loaded successfully."""
    mock_woke_df = pd.DataFrame({
        "Game": ["Bloons TD 6", "Starfield"],
        "Review": ["Contains overtly pro-LGBTQ+ messaging.", "Contains subtly pro-DEI messaging."]
    })

    mock_dirname.return_value = "/fake/path"
    mock_join.return_value = "/fake/path/woke_content_detector_full.csv"
    mock_read_csv.return_value = mock_woke_df

    result = load_woke_data()

    mock_dirname.assert_called_once()
    mock_join.assert_called_once_with(
        "/fake/path", "..", "extract", "woke_content_detector_full.csv")
    mock_read_csv.assert_called_once_with(
        "/fake/path/woke_content_detector_full.csv")
    assert "Game", "Review" in result
    assert "Bloons TD 6", "Starfield" in result


@patch("clean_csvs.os.path.join")
@patch("clean_csvs.os.path.dirname")
@patch("clean_csvs.pd.read_csv")
def test_load_rawg_data(mock_read_csv, mock_dirname, mock_join):
    """Tests rawg data is loaded successfully."""
    mock_woke_df = pd.DataFrame({
        "Name": ["VVVVVV", "Bug Princess"],
        "Release Year": ["2016.", "2020"]
    })

    mock_dirname.return_value = "/fake/path"
    mock_join.return_value = "/fake/path/rawg_video_games.csv"
    mock_read_csv.return_value = mock_woke_df

    result = load_rawg_data()

    mock_dirname.assert_called_once()
    mock_join.assert_called_once_with(
        "/fake/path", "..", "extract", "rawg_video_games.csv")
    mock_read_csv.assert_called_once_with(
        "/fake/path/rawg_video_games.csv")
    assert "Name", "Release Year" in result
    assert "VVVVV", "2016" in result


@patch("clean_csvs.load_woke_data")
def test_clean_woke_content_detector_column_renaming_valid(mock_load_data):
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

    expected_columns = ["Game", "Release Year",
                        "Developer", "Publisher", "Rating", "Review"]
    assert all(col in result.columns for col in expected_columns)


@patch("clean_csvs.load_woke_data")
def test_clean_woke_content_detector_special_characters_valid(mock_load_data):
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

    expected_df = pd.DataFrame({
        "Game": ["Assassin's Creed(Remastered)III", "Starfield"],
        "Release Year": ["2023", "2020"],
        "Developer": ["Ninja-Kiwi", "Nintendo"],
        "Publisher": ["Ninja-Kiwi.", "Nintendo "],
        "Rating": ["Not Recommended", "Not Recommended"],
        "Review": ["Contains overtly pro-LGBTQ+ messaging.", "Contains subtly pro-DEI messaging."]
    }).iloc[1:].reset_index(drop=True)

    pd.testing.assert_frame_equal(result, expected_df)


@patch("clean_csvs.load_rawg_data")
def test_clean_rawg_data_special_characters(mock_load_data):
    """Tests that special characters in RAWG data are cleaned correctly."""

    test_df = pd.DataFrame({
        "Game": ["Assassin’s Creed III", "Star–Field"],
        "Release Year": ["2023", "2020"],
        "RAWG Rating": ["3.51", "2.90"],
        "Metacritic Rating": ["78.0.", "71.0"]
    })

    mock_load_data.return_value = test_df

    result = clean_rawg_data()

    expected_df = pd.DataFrame({
        "Game": ["Assassin's Creed III", "Star-Field"],
        "Release Year": ["2023", "2020"],
        "RAWG Rating": ["3.51", "2.90"],
        "Metacritic Rating": ["78.0.", "71.0"]
    })

    pd.testing.assert_frame_equal(result, expected_df)
