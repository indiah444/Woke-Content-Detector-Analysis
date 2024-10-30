import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO


def download_woke_csv(url: str):
    """Downloads the Woke Content Detector list as a CSV."""

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")

    df = pd.read_html(StringIO(str(table)))[0]

    csv_file_path = "woke_content_detector.csv"
    df.to_csv(csv_file_path, index=False)

    print(f"CSV file downloaded successfully and saved to {csv_file_path}")


if __name__ == "__main__":

    download_woke_csv(
        "https://docs.google.com/spreadsheets/d/1AVTZPJij5PQmlWAkYdDahBrxDiwqWMGsWEcEnpdKTa4")
