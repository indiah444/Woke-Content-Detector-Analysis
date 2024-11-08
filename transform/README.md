# Transformation Folder

## Overview

This folder is responsible for transforming the data extracted in the `extract` folder. 

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

## Files

- `clean_csvs.py` takes the CSVs downloaded in the extraction process and cleans them to remove any unwanted characters, null values etc.

This folder also makes use of logging. The configuration for this can be found in the `logging_config.py` file in the `utils` folder.