import os
import pandas

from app.services.tmdb_client import TMDBClient
from app.config import FILES_DIR
from app.data_base import data_base
from app.models import Movie, Genre, Director, WatchLog


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


# ----------------------------------------------------------------------------------------------------------------------

def transform_and_load(movies, df_watched, df_diary):
    db_movies = data_base.session.query(Movie.title, Movie.release_year).all()
    db_movies_set = {(movie.title, movie.release_year) for movie in db_movies}

    enrich_list = []
    for movie in movies:
        year = int(movie["release_year"]) if movie["release_year"] else None
        title = movie["title"]
        if (title, year) not in db_movies_set:
            enrich_list.append(movie)

    if len(enrich_list) != 0:
        client = TMDBClient(os.getenv("API_KEY"))

        enriched_data = []
        enriched_data = client.fetch_movies_parallel(enrich_list)

        df_enriched = pandas.DataFrame(enriched_data)
        df_watched_enriched = df_watched.merge(df_enriched, how="left", on=["Name", "Year"]).dropna(subset="Genres")

        for i, movie in df_watched_enriched.iterrows():
            save_enriched_movie(movie)

    save_diary_logs(df_diary)

    return None


def save_enriched_movie(movie):
    genre_references = []
    for genre in movie["Genres"].split(","):
        clean_name = genre.strip()
        db_genre = data_base.session.query(Genre).filter_by(name=clean_name).first()
        if not db_genre:
            db_genre = Genre(name=clean_name)
            data_base.session.add(db_genre)
            data_base.session.flush()
        genre_references.append(db_genre)

    director_references = []
    for director in movie["Directors"].split(","):
        clean_name = director.strip()
        db_director = Director.query.filter_by(name=clean_name).first()
        if not db_director:
            db_director = Director(name=clean_name)
            data_base.session.add(db_director)
            data_base.session.flush()
        director_references.append(db_director)

    decade_str = f"{(int(movie["Year"]) // 10 * 10)}s"
    new_movie = Movie(
        title=movie["Name"],
        release_year=movie["Year"],
        poster_url=movie["Poster"],
        overview=movie["Overview"],
        country=movie["Country"],
        original_language=movie["Original Language"],
        decade=decade_str
    )

    new_movie.genres = genre_references
    new_movie.directors = director_references
    data_base.session.add(new_movie)

    data_base.session.commit()


def save_diary_logs(df_diary):
    db_movies = Movie.query.with_entities(Movie.id, Movie.title, Movie.release_year).all()
    movie_id_map = {(movie.title, movie.release_year): movie.id for movie in db_movies}

    WatchLog.query.delete()

    for i, movie in df_diary.iterrows():
        title = movie["Name"]
        release_year = int(movie["Year"]) if movie["Year"] else None

        movie_id = movie_id_map.get((title, release_year))
        if movie_id is not None:
            new_watch_log = WatchLog(
                movie_id=movie_id,
                watched_date=movie["Watched Date"],
                rating=movie["Rating"],
                is_rewatch=movie["Rewatch"],
                year_month = str(movie["Year_Month"]),
                watched_year = int(movie["Watched_Year"]),
                day_of_week = movie["Day_Of_Week"],
                time_lag = int(movie["Time_Lag"])
            )
            data_base.session.add(new_watch_log)

    data_base.session.commit()

    return None



# ----------------------------------------------------------------------------------------------------------------------

def get_processed_data():
    df_diary = process_diary()
    df_rating = process_ratings()
    df_watched, movies = process_watched()

    return df_diary, df_rating, df_watched, movies
