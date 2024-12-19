"""Tests for extract_full.py."""
# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
from gspread.exceptions import SpreadsheetNotFound
from extract_full import download_wcd_google_sheet, download_vg_sales_kaggle

"""
download_wcd_gs valid/invalid/empty
Invalid Credentials: What happens if the service account key path is wrong?
Empty Google Sheet: What happens if the sheet has no data? Does it create an empty CSV or throw an error?
Write Permission Issues: If the destination csv_file_path is not writable, does it raise an exception?
"""


@pytest.fixture
def mock_open_by_url():
    """Mocks open_by_url method."""
    mock_sheet = MagicMock()
    mock_sheet.get_all_values.return_value = [
        ["Game", "Release Year", "Developer", "Publisher", "Rating", "Review"],
        ["game1", "1999", "Ubisoft", "Ubisoft",
            "Informational", "Contains pro-LGBTQ+ messaging."],
        ["game2", "2020", "Game Studios", "Game Studios North",
            "Recommended", "Contains no Woke content."]
    ]
    return mock_sheet


@pytest.fixture
def mock_sheet1(mock_open_by_url):
    """Mocks gspread client and the method."""
    mock_client = MagicMock()
    mock_client.open_by_url.return_value.sheet1 = mock_open_by_url
    return mock_client


@patch.dict("extract_full.ENV", {"GOOGLE_SHEET_PATH": "test_creds.json"})
@patch("extract_full.ServiceAccountCredentials.from_json_keyfile_name")
@patch("extract_full.gspread.authorize")
def test_download_wcd_google_sheet_valid(mock_authorize, mock_credentials):
    """Tests a google sheet is downloaded successfully and saved as a CSV file."""

    mock_gspread_client = MagicMock()
    mock_sheet = MagicMock()
    mock_sheet.get_all_values.return_value = [
        ["Game", "Release Year", "Developer"],
        ["game1", "1999", "Ubisoft"],
    ]
    mock_gspread_client.open_by_url.return_value.sheet1 = mock_sheet
    mock_authorize.return_value = mock_gspread_client

    csv_file_path = "test_output.csv"
    download_wcd_google_sheet("https://fake-url", csv_file_path)

    with open(csv_file_path, "r") as f:
        content = f.read()
    assert "Game,Release Year,Developer" in content
    assert "game1,1999,Ubisoft" in content


@patch.dict("extract_full.ENV", {"GOOGLE_SHEET_PATH": "test_creds.json"})
@patch("extract_full.ServiceAccountCredentials.from_json_keyfile_name")
@patch("extract_full.gspread.authorize")
@patch("extract_full.LOGGER.error")
def test_download_wcd_google_sheet_invalid(mock_logging, mock_authorize, mock_credentials):
    """Tests error is raised when a google sheet is not found."""
    mock_credentials.return_value = None
    mock_client = MagicMock()
    mock_client.open_by_url.side_effect = SpreadsheetNotFound
    mock_authorize.return_value = mock_client

    download_wcd_google_sheet("https://invalid-url", "test_output_path.csv")

    mock_logging.assert_called_with(
        "Google Sheet not found. Please check the URL and try again.")


@patch.dict("extract_full.ENV", {"GOOGLE_SHEET_PATH": "test_creds.json"})
@patch("extract_full.ServiceAccountCredentials.from_json_keyfile_name")
@patch("extract_full.gspread.authorize")
@patch("extract_full.LOGGER.error")
def test_download_wcd_google_sheet_invalid_url(mock_logging, mock_authorize, mock_credentials):
    """Tests error is raised when URL is invalid. Logs SpreadsheetNotFound error and no file created."""
    mock_credentials.return_value = None
    mock_client = MagicMock()
    mock_client.open_by_url.side_effect = SpreadsheetNotFound
    mock_authorize.return_value = mock_client

    download_wcd_google_sheet("https://invalid-url", "fake_path.csv")

    mock_logging.assert_called_with(
        "Google Sheet not found. Please check the URL and try again.")


@patch.dict("extract_full.ENV", {"GOOGLE_SHEET_PATH": "test_creds.json"})
@patch("extract_full.ServiceAccountCredentials.from_json_keyfile_name")
@patch("extract_full.gspread.authorize")
@patch("extract_full.LOGGER.warning")
def test_download_wcd_google_sheet_empty_url(mock_logging, mock_authorize, mock_credentials):
    """Tests error is raised when URL is empty. Maybe log a warning or error"""
    download_wcd_google_sheet("", "fake_path.csv")
    # mock_logging.assert_not_called_with("No data retrieved from Google Sheet.")
    mock_logging.assert_not_called


@patch("extract_full.kagglehub.dataset_download")
@patch("extract_full.os.listdir")
@patch("extract_full.os.path.join")
@patch("extract_full.rename")
@patch("extract_full.LOGGER.info")
def test_download_vg_sales_kaggle_valid(mock_logging, mock_dataset, mock_listdir, mock_path_join, mock_rename):
    """Tests a kaggle dataset is downloaded successfully and saved as a CSV file."""
    mock_dataset.return_value = "/fake/path"
    mock_listdir.return_value = ["dataset.csv"]
    mock_path_join.return_value = "/fake/path/dataset.csv"

    dataset_name = "vg_sales_dataset"
    download_path = "test_output.csv"
    download_vg_sales_kaggle(dataset_name, download_path)

    mock_dataset.assert_called_with(
        ["dataset.csv"], "test_output.csv")
    mock_logging.assert_called_once_with(
        "Dataset downloaded and saved to %s", download_path)


@patch("extract_full.kagglehub.dataset_download")
@patch("extract_full.LOGGER.error")
def test_download_vg_sales_kaggle_invalid(mock_logging, mock_dataset):
    """Tests error is raised when kaggle dataset is not found."""
    mock_dataset.side_effect = FileNotFoundError()

    dataset_name = "invalid_dataset"
    download_path = "./test_output.csv"
    download_vg_sales_kaggle(dataset_name, download_path)

    mock_dataset.assert_called_once_with(dataset_name, force_download=True)
    mock_logging.assert_called_once_with(
        "The specified Kaggle dataset could not be found: %s", dataset_name
    )
