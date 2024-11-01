"""A file to extract the entire Woke Content Detector list and other datasets to CSVs."""

import os
from os import environ as ENV
from os import rename
import gspread
import pandas as pd
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import kagglehub


def download_wcd_google_sheet(sheet_url, csv_file_path):
    """Download the Woke Content Detector data from a Google Sheet and save it as CSV."""

    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    json_key_path = ENV["GOOGLE_SHEET_PATH"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        json_key_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(sheet_url).sheet1

    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])

    df.to_csv(csv_file_path, index=False)
    print(f"CSV file downloaded successfully and saved to {csv_file_path}")


def download_vg_sales_kaggle(dataset_name: str, download_path: str):
    """Download data from a Kaggle dataset and save it as a CSV."""

    load_dotenv()

    dataset_folder_path = kagglehub.dataset_download(
        dataset_name, force_download=True)

    downloaded_file_path = os.path.join(
        dataset_folder_path, os.listdir(dataset_folder_path)[0])

    rename(downloaded_file_path, download_path)
    print(f"Dataset downloaded and saved to {download_path}")


if __name__ == "__main__":

    load_dotenv()

    google_sheet = "https://docs.google.com/spreadsheets/d/1AVTZPJij5PQmlWAkYdDahBrxDiwqWMGsWEcEnpdKTa4/edit?gid=0"
    wcd_csv_filepath = "woke_content_detector_full.csv"
    download_wcd_google_sheet(google_sheet, wcd_csv_filepath)

    vg_dataset_name = "gregorut/videogamesales"
    vg_csv_filepath = "videogame_sales.csv"
    download_vg_sales_kaggle(vg_dataset_name, vg_csv_filepath)
