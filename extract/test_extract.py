"""Tests for extract.py."""
# pylint: skip-file
from unittest.mock import patch, MagicMock
import pandas as pd
from extract import download_woke_csv


@patch("extract.requests.get")
@patch("extract.BeautifulSoup")
@patch("extract.pd.read_html")
@patch("extract.pd.DataFrame.to_csv")
def test_download_woke_csv_valid(mock_to_csv, mock_read_html, mock_beautiful_soup, mock_requests):
    """Tests that the CSV is downloaded and saved successfully."""
    mock_requests.return_value.text = "<html><table><tr><td>Data</td></tr></table></html>"
    mock_soup = MagicMock()
    mock_soup.find.return_value = "<table><tr><td>Data</td></tr></table>"
    mock_beautiful_soup.return_value = mock_soup

    mock_df = pd.DataFrame({"Column": ["Data"]})
    mock_read_html.return_value = [mock_df]

    download_woke_csv("https://test.com")

    mock_requests.assert_called_once_with("https://test.com", timeout=10)
    mock_beautiful_soup.assert_called_once()
    mock_to_csv.assert_called_once_with(
        "woke_content_detector.csv", index=False)


# @patch("extract.requests.get")
# @patch("extract.BeautifulSoup")
# def test_download_woke_csv_no_table(mock_beautiful_soup, mock_requests):
#     """Tests error raised when no table is found in the HTML."""
#     mock_requests.return_value.text = "<html></html>"
#     mock_soup = MagicMock()
#     mock_soup.find.return_value = None
#     mock_beautiful_soup.return_value = mock_soup
