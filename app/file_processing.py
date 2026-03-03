import os
import pandas as pandas
from werkzeug.utils import secure_filename
from .config import DATA_DIR, EXPECTED_DATA

def validate_files(files: list):
    file_names = [file.filename for file in files if file.filename]
    expected_names = EXPECTED_DATA.keys()

    if (len(file_names) != len(expected_names)) or (set(file_names) != expected_names):
        return False, "Arquivos inválidos"

    for file in files:
        filename = file.filename
        expected_columns = set(EXPECTED_DATA[filename])

        try:
            file_columns = set(pandas.read_csv(file.stream, nrows=0))

            if expected_columns != file_columns: return False, "Um ou mais arquivos possuem colunas inválidas"

            file.seek(0)
        except Exception:
            print(f"Erro ao processar {filename}")
            return False, "Um ou mais arquivos estão corrompidos ou não são um CSV válido"
        except pandas.errors.EmptyDataError:
            print(f"O arquivo '{filename}' está vazio.")
            return False, "Um ou mais arquivos estão vazios"

    return True, "OK"

#-----------------------------------------------------------------------------------------------------------------------

def save_files(files: list):
    for file in files:
        if file.filename in EXPECTED_DATA.keys():
            safe_file_name = secure_filename(file.filename)
            path = os.path.join(DATA_DIR, safe_file_name)
            file.save(path)