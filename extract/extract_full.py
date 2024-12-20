"""A file to extract the entire Woke Content Detector list and other datasets to CSVs."""

import os
from os import environ as ENV
from os import rename
import logging

import gspread
from gspread.exceptions import SpreadsheetNotFound
import pandas as pd
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import kagglehub

from utils.logging_config import logger_setup


LOGGER = logging.getLogger(__name__)

WCD_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1AVTZPJij5PQmlWAkYdDahBrxDiwqWMGsWEcEnpdKTa4/edit?gid=0"
WCD_CSV_FILEPATH = "woke_content_detector_full.csv"

VG_DATASET_NAME = "gregorut/videogamesales"
VG_CSV_FILEPATH = "videogame_sales.csv"


def download_wcd_google_sheet(sheet_url, csv_file_path):
    """Download the Woke Content Detector data from a Google Sheet and save it as CSV."""

    if not sheet_url:
        LOGGER.error(
            "The Google Sheet URL is empty. Please provide a valid URL.")
        return

    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        json_key_path = ENV.get("GOOGLE_SHEET_PATH")
        if not json_key_path:
            LOGGER.error(
                "The GOOGLE_SHEET_PATH environment variable is missing.")
            return

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            json_key_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url).sheet1
        data = sheet.get_all_values()

        if not data or len(data) <= 1:
            LOGGER.warning("No valid data retrieved from Google Sheet.")
            return

        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_csv(csv_file_path, index=False)
        LOGGER.info(
            "CSV file downloaded successfully and saved to %s", csv_file_path)

    except SpreadsheetNotFound:
        LOGGER.error(
            "Google Sheet not found. Please check the URL and try again.")
    except FileNotFoundError as e:
        LOGGER.error("Error with credentials file: %s", e)


def download_vg_sales_kaggle(dataset_name: str, download_path: str):
    """Download data from a Kaggle dataset and save it as a CSV."""
    try:
        dataset_folder_path = kagglehub.dataset_download(
            dataset_name, force_download=True)
        files = os.listdir(dataset_folder_path)

        if not files:
            LOGGER.warning(
                "Kaggle dataset folder is empty - No files to process.")
            return

        downloaded_file_path = os.path.join(dataset_folder_path, files[0])
        rename(downloaded_file_path, download_path)
        LOGGER.info("Dataset downloaded and saved to %s", download_path)

    except FileNotFoundError:
        LOGGER.error(
            "The specified Kaggle dataset could not be found: %s", dataset_name)


if __name__ == "__main__":

    logger_setup("extract_full_log.log", "logs")
    load_dotenv()
    LOGGER.info("Loading environment variables from .env file.")

    LOGGER.info("Starting data extraction process.")
    download_wcd_google_sheet(WCD_GOOGLE_SHEET, WCD_CSV_FILEPATH)
    download_vg_sales_kaggle(VG_DATASET_NAME, VG_CSV_FILEPATH)
    LOGGER.info("Data extraction process completed.")
