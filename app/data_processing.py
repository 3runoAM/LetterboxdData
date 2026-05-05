import os
import pandas
from .config import FILES_DIR, BASE_DIR


def process_diary():
    df_diary = pandas.read_csv(os.path.join(FILES_DIR, "diary.csv"))

    del df_diary["Letterboxd URI"]
    del df_diary["Tags"]

    df_diary["Watched Date"] = pandas.to_datetime(df_diary["Watched Date"], errors="coerce")
    df_diary = df_diary.dropna(subset=["Watched Date"]).copy()

    df_diary["Year"] = pandas.to_numeric(df_diary["Year"], errors="coerce")
    df_diary["Rewatch"] = df_diary["Rewatch"].fillna("No").map({"Yes": True, "No": False})

    df_diary["Year_Month"] = df_diary["Watched Date"].dt.to_period("M").astype(str)
    df_diary["Watched_Year"] = df_diary["Watched Date"].dt.year
    df_diary["Day_Of_Week"] = df_diary["Watched Date"].dt.day_name()
    df_diary["Time_Lag"] = df_diary["Watched_Year"] - df_diary["Year"]

    return df_diary

# -----------------------------------------------------------------------------------------------------------------------

def process_ratings():
    df_ratings = pandas.read_csv(os.path.join(FILES_DIR, "ratings.csv"))

    del df_ratings["Letterboxd URI"]

    df_ratings["Rating"] = pandas.to_numeric(df_ratings["Rating"], errors="coerce")
    df_ratings["Year"] = pandas.to_numeric(df_ratings["Year"], errors="coerce")

    df_ratings = df_ratings.dropna(subset=["Rating", "Year"]).copy()

    df_ratings["Decade"] = (df_ratings["Year"] // 10 * 10).astype(int).astype(str) + "s"

    return df_ratings

# -----------------------------------------------------------------------------------------------------------------------

def process_watched():
    df_watched = pandas.read_csv(os.path.join(FILES_DIR, "watched.csv"))

    df_watched["Date"] = pandas.to_datetime(df_watched["Date"], errors="coerce")
    df_watched = df_watched.dropna(subset=["Date"]).copy()

    df_watched["Year"] = pandas.to_numeric(df_watched["Year"], errors="coerce")

    movies = df_watched[["Name", "Year", "Letterboxd URI"]].drop_duplicates().dropna()
    movies = movies.rename(columns={"Name": "title", "Year": "release_year"}).to_dict(orient="records")

    return df_watched, movies

# -----------------------------------------------------------------------------------------------------------------------

def get_processed_data():
    df_diary = process_diary()
    df_rating = process_ratings()
    df_watched, movies = process_watched()

    return df_diary, df_rating, df_watched, movies