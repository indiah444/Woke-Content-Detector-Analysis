# Extraction folder

## Overview

This folder is responsible for extracting the various datasets associated with this project. The datasets currently originate from both Google Sheets and Kaggle.

## Setup

1. Create a virtual environment and activate it.

```sh
python3 -m venv venv
source venv/bin/activate
```

2. Install the necessary requirements.

```sh
pip install -r requirements.txt
```

3. Create an `.env` file and fill it with the following environment variables:

```env
# Google Sheets configuration
GOOGLE_SHEET_PATH=XXXXXXX

# Kaggle configuration
KAGGLE_USERNAME=XXXXXXX
KAGGLE_KEY=XXXXXXX
```

The `GOOGLE_SHEET_PATH` variable refers to the credentials necessary to use the Google Sheets API. The type of credentials used in this project are the Service Account credentials. More information on how to download these credentials can be found [here](https://developers.google.com/workspace/guides/create-credentials).

The `KAGGLE_USERNAME` and `KAGGLE_KEY` variables refer to the credentials necessary to use the Kaggle API. Documentation on this can be found [here](https://www.kaggle.com/docs/api).


## Files

- `extract.py` downloads a small sample of the Woke Content Detector list (100 rows). Helpful for initial data exploration.
- `extract_full.py` downloads the entire Woke Content Detector list and other Kaggle datasets and saves them as CSVs.
- `logging_config.py` contains the necessary config to set up logging for this folder.




