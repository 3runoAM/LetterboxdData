import os
import pandas
from .config import DATA_DIR, BASE_DIR


def process_diary():
    df_diary = pandas.read_csv(os.path.join(DATA_DIR, "diary.csv"))

    df_diary['Watched Date'] = pandas.to_datetime(df_diary['Watched Date'], errors='coerce')
    df_diary = df_diary.dropna(subset=['Watched Date']).copy()

    df_diary['Year'] = pandas.to_numeric(df_diary['Year'], errors='coerce')
    df_diary['Rewatch'] = df_diary['Rewatch'].fillna('No').map({'Yes': True, 'No': False})

    # Todo: Criar script próprio para enriquecer os dados quando for se comunicar com a API ao invés de fazer isso na hora de carregar/tipar os dados
    df_diary['Ano_Mes'] = df_diary['Watched Date'].dt.to_period('M').astype(str)
    df_diary['Ano_Assistido'] = df_diary['Watched Date'].dt.year
    df_diary['Dia_da_Semana'] = df_diary['Watched Date'].dt.day_name()
    df_diary['Time_Lag'] = df_diary['Ano_Assistido'] - df_diary['Year']

    return df_diary

#-----------------------------------------------------------------------------------------------------------------------

def process_ratings():
    df_ratings = pandas.read_csv(os.path.join(DATA_DIR, "ratings.csv"))

    df_ratings['Rating'] = pandas.to_numeric(df_ratings['Rating'], errors='coerce')
    df_ratings['Year'] = pandas.to_numeric(df_ratings['Year'], errors='coerce')

    df_ratings = df_ratings.dropna(subset=['Rating', 'Year']).copy()

    # Todo: Criar script próprio para enriquecer os dados quando for se comunicar com a API ao invés de fazer isso na hora de carregar/tipar os dados
    df_ratings['Decade'] = (df_ratings['Year'] // 10 * 10).astype(int).astype(str) + "s"

    return df_ratings

#-----------------------------------------------------------------------------------------------------------------------

def process_watched():
    df_watched = pandas.read_csv(os.path.join(DATA_DIR, "watched.csv"))

    df_watched['Date'] = pandas.to_datetime(df_watched['Date'], errors='coerce')
    df_watched = df_watched.dropna(subset=['Date']).copy()

    df_watched['Year'] = pandas.to_numeric(df_watched['Year'], errors='coerce')

    return df_watched

#-----------------------------------------------------------------------------------------------------------------------

def get_processed_data():
    df_diary = process_diary()
    df_rating = process_ratings()
    df_watched = process_watched()

    return df_diary, df_rating, df_watched