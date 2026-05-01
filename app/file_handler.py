import os
import pandas as pandas
from werkzeug.utils import secure_filename
from .config import DATA_DIR, EXPECTED_DATA

def validate_files(files: list):
    file_names = [file.filename for file in files if file.filename]
    expected_names = set(EXPECTED_DATA.keys())

    if (len(file_names) != len(expected_names)) or (set(file_names) != expected_names):
        return False, "Invalid files"

    for file in files:
        filename = file.filename
        expected_columns = set(EXPECTED_DATA[filename])

        try:
            file_columns = set(pandas.read_csv(file.stream, nrows=0).columns)

            if expected_columns != file_columns:
                return False, "One or more files have invalid columns"

            file.stream.seek(0)
        except pandas.errors.EmptyDataError:
            print(f"File `{filename}` is empty.")
            return False, "One or more files are empty"
        except Exception:
            print(f"Error processing `{filename}`")
            return False, "One or more files are corrupted or are not a valid CSV"

    return True, "OK"

#-----------------------------------------------------------------------------------------------------------------------

def save_files(files: list):
    for file in files:
        if file.filename in EXPECTED_DATA.keys():
            safe_file_name = secure_filename(file.filename)
            path = os.path.join(DATA_DIR, safe_file_name)
            file.save(path)

#-----------------------------------------------------------------------------------------------------------------------

def is_data_available():
    for filename in EXPECTED_DATA.keys():
        if not os.path.exists(os.path.join(DATA_DIR, filename)):
            return False
    return True

def is_data_processed():
    processed_files = ["df_diary.csv", "df_rating.csv", "df_watched.csv", "df_watched_enriched.csv"]
    for filename in processed_files:
        if not os.path.exists(os.path.join(DATA_DIR, filename)):
            return False
    return True