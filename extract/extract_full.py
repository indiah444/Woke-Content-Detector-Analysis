"""A file to extract the entire Woke Content Detector list to a CSV."""

from os import environ as ENV
import gspread
import pandas as pd
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


def download_google_sheet(sheet_url, csv_file_path):
    """Download data from Google Sheet and save it as CSV."""

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


if __name__ == "__main__":

    load_dotenv()

    google_sheet = "https://docs.google.com/spreadsheets/d/1AVTZPJij5PQmlWAkYdDahBrxDiwqWMGsWEcEnpdKTa4/edit?gid=0"
    csv_filepath = "woke_content_detector_full.csv"
    download_google_sheet(google_sheet, csv_filepath)
