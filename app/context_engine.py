import pandas
from pandas.core.methods import describe


def get_total_movies(df_watched):
    return df_watched.shape[0]


def get_average_rating(df_rating):
    return round(df_rating["Rating"].mean(), 1)


def get_favorite_day(df_diary):
    favorite_day = df_diary["da_of_week"].mode()[0]

    return favorite_day


def get_favorite_decade(df_ratings):
    decades = df_ratings.groupby("Decade").agg(
        Average=("Rating", "mean"),
        Count=("Rating", "count")
    )

    valid_decades = decades[decades["Count"] >= 5]

    if valid_decades.empty:
        return None

    favorite_decade = valid_decades["Average"].idxmax()

    return favorite_decade


def get_favorite_genre(df_watched_enriched):
    if df_watched_enriched is not None:
        common_genres = df_watched_enriched["Genres"].str.split(",").explode().str.strip()

        if not common_genres.empty:
            return common_genres.value_counts().index[0]

        return None
    return None


def get_most_frequent_director(df_watched_enriched):
    if df_watched_enriched is not None:
        common_directors = df_watched_enriched["Directors"].str.split(",").explode().str.strip()

        if not common_directors.empty:
            return common_directors.value_counts().index[0]
        return None
    return None


def get_rewatch_context(df_diary, df_watched_enriched):
    total_diary = len(df_diary)
    total_rewatches = df_diary["Rewatch"].sum()
    rewatch_rate = (total_rewatches / total_diary) * 100 if total_diary > 0 else 0

    if rewatch_rate >= 40:
        rewatch_profile = "Resident"
        rewatch_description = f"Some people watch movies; you live in them. Your {rewatch_rate:.1f}% rewatch rate proves that a masterpiece only gets better with the 2nd viewing onwards"
    elif rewatch_rate >= 15:
        rewatch_profile = "Curator"
        rewatch_description = f"You aren't afraid of new discoveries, but your {rewatch_rate:.1f}% rewatch rate shows that you never truly abandon your comfort films"
    elif rewatch_rate >= 5:
        rewatch_profile = "Explorer"
        rewatch_description = f"The world is too big to spend time watching the same thing twice, right? With {rewatch_rate:.1f}% rewatch rate, you prefer to keep moving forward and discover new stories"
    else:
        rewatch_profile = "Trailblazer"
        rewatch_description = f"\"Never look back\" is your motto for life. Your eyes are always on the horizon with {rewatch_rate:.1f}% rewatch rate"

    # ------------------------------------------------------------------
    rewatched_movies = None
    if df_watched_enriched is not None:
        df_rewatch = df_diary[df_diary["Rewatch"] == True]

        if not df_rewatch.empty:
            df_movies_rewatch = pandas.merge(df_rewatch, df_watched_enriched[["Name", "Year", "Poster"]],
                                             on=["Name", "Year"], how="left").sort_values(by="Rating", ascending=False)

            rewatched_movies = df_movies_rewatch[["Name", "Year", "Poster", "Rating"]].to_dict(orient="records")

    return {
        "rewatch_profile": rewatch_profile,
        "rewatch_description": rewatch_description,
        "rewatched_movies": rewatched_movies
    }


def get_streak_context(df_diary, df_watched_enriched):
    dates = df_diary["Watched Date"].drop_duplicates().sort_values(ignore_index=True)

    if dates.empty:
        return {"days": 0, "start": None, "end": None}

    is_not_consecutive = dates.diff() != pandas.Timedelta(days=1)

    streak_ids = is_not_consecutive.cumsum()

    streaks = dates.groupby(streak_ids).agg(["count", "min", "max"])
    longest = streaks.loc[streaks["count"].idxmax()]

    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    def format_date(date_obj):
        if pandas.isna(date_obj):
            return None
        return f"{months[int(date_obj.month)]} {int(date_obj.day)}, {int(date_obj.year)}"

    streak_movies = None
    if df_watched_enriched is not None and longest["count"] > 1:
        streak_mask = (df_diary["Watched Date"] >= longest["min"]) & (df_diary["Watched Date"] <= longest["max"])
        df_streak_movies = df_diary[streak_mask]

        df_streak_movies = pandas.merge(df_streak_movies, df_watched_enriched[["Name", "Year", "Poster"]],
                                        on=["Name", "Year"], how="left").sort_values(by="Rating", ascending=False)

        streak_movies = df_streak_movies[["Name", "Year", "Poster", "Rating"]].to_dict(orient="records")

    return {
        "days": int(longest["count"]),
        "start": format_date(longest["min"]),
        "end": format_date(longest["max"]),
        "movies": streak_movies,
    }


def get_movie_moment_context(df_diary, df_watched_enriched):
    df_master = pandas.merge(
        df_diary[["Name", "Year", "Rating", "da_of_week"]],
        df_watched_enriched[["Name", "Year", "Genres"]],
        on=["Name", "Year"]
    )

    total_movies = len(df_master)

    favorite_day = df_master["da_of_week"].mode()[0]
    df_movies_from_favorite_day = df_master[df_master["da_of_week"] == favorite_day].copy()

    total_movies_from_favorite_day = len(df_movies_from_favorite_day)
    movie_percentage = (total_movies_from_favorite_day / total_movies) * 100

    df_movies_from_favorite_day["Genres"] = df_movies_from_favorite_day["Genres"].str.split(",")
    df_genres_exploded = df_movies_from_favorite_day.explode("Genres")
    df_genres_exploded["Genres"] = df_genres_exploded["Genres"].str.strip()

    top_genre = df_genres_exploded["Genres"].mode()[0]
    df_final_subset = df_genres_exploded[df_genres_exploded["Genres"] == top_genre].copy()

    df_final_subset["Decade"] = (df_final_subset["Year"] // 10 * 10).astype(str) + "s"
    top_decade = df_final_subset["Decade"].mode()[0]

    return {
        "favorite_day": favorite_day.lower(),
        "favorite_genre": top_genre.lower(),
        "favorite_decade": top_decade,
        "movie_percentage": round(movie_percentage, 1),
    }


def get_context(df_watched, df_diary, df_ratings, df_watched_enriched=None):
    total_movies = {"label": "Movies Watched", "value": get_total_movies(df_watched)}
    favorite_day = {"label": "Cinema Day", "value": get_favorite_day(df_diary)}
    favorite_decade = {"label": "Golden Decade", "value": get_favorite_decade(df_ratings)}
    average_rating = {"label": "Average Rating", "value": get_average_rating(df_ratings)}
    favorite_genre = {"label": "Go-to Genre", "value": get_favorite_genre(df_watched_enriched)}
    favorite_director = {"label": "Resident Director", "value": get_most_frequent_director(df_watched_enriched)}

    metric_list = [total_movies, favorite_day, favorite_decade, average_rating, favorite_genre, favorite_director]

    streak_context = get_streak_context(df_diary, df_watched_enriched)
    rewatch_context = get_rewatch_context(df_diary, df_watched_enriched)
    movie_context = get_movie_moment_context(df_diary, df_watched_enriched)

    return {
        "metric_list": metric_list,
        "streak_context": streak_context,
        "rewatch_context": rewatch_context,
        "movie_context": movie_context,
    }
