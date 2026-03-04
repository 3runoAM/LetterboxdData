import os
import pandas
from .config import DATA_DIR

def load_processed_diary():
    df_diary = pandas.read_csv(os.path.join(DATA_DIR, "diary.csv"))

    df_diary['Watched Date'] = pandas.to_datetime(df_diary['Watched Date'], errors='coerce')
    df_diary = df_diary.dropna(subset=['Watched Date']).copy()

    df_diary['Year'] = pandas.to_numeric(df_diary['Year'], errors='coerce')
    df_diary['Rewatch'] = df_diary['Rewatch'].fillna('No').map({'Yes': True, 'No': False})

    df_diary['Ano-Mes'] = df_diary['Watched Date'].dt.to_period('M').astype(str)
    df_diary['Ano_Assistido'] = df_diary['Watched Date'].dt.year
    df_diary['Dia_da_Semana'] = df_diary['Watched Date'].dt.day_name()

    df_diary['Time_Lag'] = df_diary['Ano_Assistido'] - df_diary['Year']

    df_diary_datas = df_diary.sort_values('Watched Date').drop_duplicates('Watched Date').copy()
    df_diary_datas['Diff'] = df_diary_datas['Watched Date'].diff().dt.days

    df_diary_datas['Streak_ID'] = (df_diary_datas['Diff'] > 1).cumsum()

    streaks = df_diary_datas.groupby('Streak_ID').size().reset_index(name='Dias_Consecutivos')

    return df_diary, streaks


def load_processed_ratings():
    df_ratings = pandas.read_csv(os.path.join(DATA_DIR, "ratings.csv"))

    df_ratings['Rating'] = pandas.to_numeric(df_ratings['Rating'], errors='coerce')
    df_ratings['Year'] = pandas.to_numeric(df_ratings['Year'], errors='coerce')
    df_ratings = df_ratings.dropna(subset=['Rating', 'Year']).copy()


    df_ratings['Decade'] = (df_ratings['Year'] // 10 * 10).astype(int).astype(str) + "s"

    return df_ratings
