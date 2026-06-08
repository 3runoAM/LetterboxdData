# CURRENT PROFILE CONTEXT ----------------------------------------------------------------------------------------------
import calendar
from collections import Counter
from datetime import date, timedelta

from sqlalchemy.orm import joinedload

from app import data_base
from app.models import WatchLog, Movie


def get_current_time():
    today_obj = date.today()

    days_until_sunday = (today_obj.weekday() + 1) % 7

    start_week = today_obj - timedelta(days=days_until_sunday)
    week_ends = start_week + timedelta(days=6)

    month_start = date(today_obj.year, today_obj.month, 1)

    last_day_month = calendar.monthrange(today_obj.year, today_obj.month)[1]
    month_ends = date(today_obj.year, today_obj.month, last_day_month)

    year_start = date(today_obj.year, 1, 1)
    year_ends = date(today_obj.year, 12, 31)

    return {
        "week": {
            "start": start_week,
            "end": week_ends
        },
        "month": {
            "start": month_start,
            "end": month_ends
        },
        "year": {
            "start": year_start,
            "end": year_ends
        }
    }


def get_watched_this_year(current_time):
    return (data_base.session.query(WatchLog)
            .options(joinedload(WatchLog.movie).selectinload(Movie.genres))
            .filter(WatchLog.watched_year == current_time.get("year").get("start").year)
            .order_by(WatchLog.watched_date.desc())
            .all())


def get_watched_movies_per_period(watched_this_year, current_time):
    def to_dict(watch_log):
        return {
            "name": watch_log.movie.title,
            "poster": watch_log.movie.poster_url,
            "year": watch_log.movie.release_year,
            "rating": watch_log.rating,
            "watched_date": watch_log.watched_date,
            "genres": [genre.name for genre in watch_log.movie.genres],
            "decade": watch_log.movie.decade,
            "time_lag": watch_log.time_lag
        }

    watched_this_year = [to_dict(movie) for movie in watched_this_year]
    watched_this_year.sort(key=lambda x: x["watched_date"])

    watched_this_month = [
        movie for movie in watched_this_year if
        current_time.get("month").get("start") <= movie.get("watched_date") <= current_time.get("month").get("end")
    ]
    watched_this_month.sort(key=lambda x: x["watched_date"])

    watched_this_week = [
        movie for movie in watched_this_month if
        current_time.get("week").get("start") <= movie.get("watched_date") <= current_time.get("week").get("end")
    ]
    watched_this_week.sort(key=lambda x: x["watched_date"])

    return {
        "watched_this_year": watched_this_year,
        "watched_this_month": watched_this_month,
        "watched_this_week": watched_this_week
    }


def get_total_movies_per_period(watched_movies):
    total_year = len(watched_movies.get("watched_this_year"))
    total_month = len(watched_movies.get("watched_this_month"))
    total_week = len(watched_movies.get("watched_this_week"))

    return total_year, total_month, total_week


def get_average_rating_per_period(watched_movies):
    total_year, total_month, total_week = get_total_movies_per_period(watched_movies)

    def calculate_avg(movies, total):
        return sum(movie.get("rating") for movie in movies) / total if total > 0 else 0

    avg_rating_week = calculate_avg(watched_movies.get("watched_this_week"), total_week)
    avg_rating_month = calculate_avg(watched_movies.get("watched_this_month"), total_month)
    avg_rating_year = calculate_avg(watched_movies.get("watched_this_year"), total_year)

    return round(avg_rating_year, 1), round(avg_rating_month, 1), round(avg_rating_week, 1)


def get_favorite_genre_per_period(watched_movies):
    def calculate_top_genre(movies):
        if not movies:
            return None

        all_genres = []
        for movie in movies:
            all_genres.extend(movie.get("genres"))

        genre_count = Counter(all_genres)

        return genre_count.most_common(1)[0][0]

    fav_genre_week = calculate_top_genre(watched_movies.get("watched_this_week"))
    fav_genre_month = calculate_top_genre(watched_movies.get("watched_this_month"))
    fav_genre_year = calculate_top_genre(watched_movies.get("watched_this_year"))

    return fav_genre_year, fav_genre_month, fav_genre_week


def get_favorite_decade_per_period(watched_movies):
    def calculate_favorite_decade(movies):
        if not movies:
            return None

        decades = [movie.get("decade") for movie in movies]
        decade_count = Counter(decades)

        return decade_count.most_common(1)[0][0]

    fav_decade_week = calculate_favorite_decade(watched_movies.get("watched_this_week"))
    fav_decade_month = calculate_favorite_decade(watched_movies.get("watched_this_month"))
    fav_decade_year = calculate_favorite_decade(watched_movies.get("watched_this_year"))

    return fav_decade_week, fav_decade_month, fav_decade_year


def get_liked_disliked_per_period(watched_movies):
    def calculate_liked_disliked(movies):
        if not movies:
            return {
            "most_liked_movie": None,
            "most_disliked_movie": None,
        }

        movies.sort(key=lambda x: x["watched_date"], reverse=True)

        most_liked_rating = 0
        most_liked_movie = None

        most_disliked_rating = 5
        most_disliked_movie = None

        for movie in movies:
            if movie.get("rating") > most_liked_rating:
                most_liked_rating = movie.get("rating")
                most_liked_movie = movie
            if movie.get("rating") < most_disliked_rating:
                most_disliked_rating = movie.get("rating")
                most_disliked_movie = movie

        return {
            "most_liked_movie": most_liked_movie,
            "most_disliked_movie": most_disliked_movie,
        }

    most_liked_disliked_week = calculate_liked_disliked(watched_movies.get("watched_this_week"))
    most_liked_disliked_month = calculate_liked_disliked(watched_movies.get("watched_this_month"))
    most_liked_disliked_year = calculate_liked_disliked(watched_movies.get("watched_this_year"))

    return most_liked_disliked_week, most_liked_disliked_month, most_liked_disliked_year


def get_time_lag_context_per_period(watched_movies):
    def get_time_lag_context(movies):
        if not movies:
            return {
            "time_profile": None,
            "time_description": None,
            "time_lag_average": None
        }

        time_lags = [movie.get("time_lag") for movie in movies]
        avg_lag = sum(time_lags) / len(time_lags)

        if avg_lag >= 30:
            time_profile = "Historian"
            time_description = f"Your time machine is permanently set to the past. With an average of {avg_lag:.1f} years between release dates and your screen, you cherish the timeless classics that shaped cinema"
        elif avg_lag >= 15:
            time_profile = "Nostalgic"
            time_description = f"Your sweet spot is about {avg_lag:.1f} years back. You love revisiting or discovering those generation-defining gems that have aged like fine wine"
        elif avg_lag >= 5:
            time_profile = "Modernist"
            time_description = f"You like giving movies some room to breathe. Your {avg_lag:.1f}-year average gap shows you catch up on great stories at your own pace, away from the immediate hype"
        else:
            time_profile = "Trendsetter"
            time_description = f"You live in the absolute present. Your average gap is just {avg_lag:.1f} years—if a movie is any fresher, it would still be premiering in theaters"

        return {
            "time_profile": time_profile,
            "time_description": time_description,
            "time_lag_average": round(avg_lag, 1)
        }

    time_lag_week = get_time_lag_context(watched_movies.get("watched_this_week"))
    time_lag_month = get_time_lag_context(watched_movies.get("watched_this_month"))
    time_lag_year = get_time_lag_context(watched_movies.get("watched_this_year"))

    return time_lag_week, time_lag_month, time_lag_year


def get_genre_category_per_period(watched_movies):
    def get_genre_category(movies, time):
        if not movies:
            return {
            "categories": None,
            "values": None,
            "description": None,
        }

        genre_category_mapping = {
            "Adrenaline": ["Action", "Adventure", "War", "Western"],
            "Shiver": ["Crime", "Mystery", "Horror", "Thriller"],
            "Brain": ["Drama", "Science Fiction", "Documentary", "History"],
            "Emotion": ["Comedy", "Romance", "Family"],
            "Escapism": ["Fantasy", "Animation", "Music"]
        }

        graph_points = {category: 0 for category in genre_category_mapping.keys()}
        points = 0

        for movie in movies:
            rating = movie.get("rating")
            for genre in movie.get("genres"):
                for category, genres in genre_category_mapping.items():
                    if genre in genres:
                        graph_points[category] += rating
                        points += rating
                        break

        categories = list(genre_category_mapping.keys())
        values = [round((graph_points[category] / points) * 100, 1) for category in
                  categories] if points > 0 else [0] * len(categories)

        max_value_category = categories[values.index(max(values))]

        if max_value_category == 'Adrenaline':
            description = f"Your {time} was dominated by the Adrenaline trait: you thrived on high-octane action, fast-paced plots, and heart-pounding blockbusters that kept you on the edge of your seat"
        elif max_value_category == 'Shiver':
            description = f"Your {time} was dominated by the Shiver trait: you had a strong craving for the darker side of cinema, preferring tense thrillers, eerie mysteries, and horror stories that tested your nerves"
        elif max_value_category == 'Brain':
            description = f"Your {time} was dominated by the Brain trait: you looked for psychological depth, mind-bending sci-fi, and complex narratives that left you thinking long after the credits rolled"
        elif max_value_category == 'Emotion':
            description = f"Your {time} was dominated by the Emotion trait: you were drawn to powerful dramas, sweeping romances, and deeply moving stories crafted to touch your heart or make you shed a tear"
        elif max_value_category == 'Escapism':
            description = f"Your {time} was dominated by the Escapism trait: you loved lighthearted comedies, animated wonders, and pure fantasy—the perfect cinematic escape to unwind and unplug from reality"
        else:
            description = "Your movie taste was perfectly balanced across multiple cinematic dimensions!"

        return {
            "categories": categories,
            "values": values,
            "description": description,
        }

    genre_category_week = get_genre_category(watched_movies.get("watched_this_week"), "week")
    genre_category_month = get_genre_category(watched_movies.get("watched_this_month"), "month")
    genre_category_year = get_genre_category(watched_movies.get("watched_this_year"), "year")


    return genre_category_week, genre_category_month, genre_category_year


def get_current_profile_context():
    current_time = get_current_time()
    watched_this_year = get_watched_this_year(current_time)

    watched_movies = get_watched_movies_per_period(watched_this_year, current_time)

    total_year, total_month, total_week = get_total_movies_per_period(watched_movies)
    average_year, average_month, average_week = get_average_rating_per_period(watched_movies)
    fav_genre_year, fav_genre_month, fav_genre_week = get_favorite_genre_per_period(watched_movies)
    fav_decade_week, fav_decade_month, fav_decade_year = get_favorite_decade_per_period(watched_movies)

    total_movies_year = {"label": "Movies Watched", "value": total_year}
    average_year = {"label": "Average Rating", "value": average_year}
    fav_genre_year = {"label": "Go-to Genre", "value": fav_genre_year}
    fav_decade_year = {"label": "Golden Decade", "value": fav_decade_year}
    metrics_list_year = [total_movies_year, average_year, fav_genre_year, fav_decade_year]

    total_movies_month = {"label": "Movies Watched", "value": total_month}
    average_month = {"label": "Average Rating", "value": average_month}
    fav_genre_month = {"label": "Go-to Genre", "value": fav_genre_month}
    fav_decade_month = {"label": "Golden Decade", "value": fav_decade_month}
    metrics_list_month = [total_movies_month, average_month, fav_genre_month, fav_decade_month]

    total_movies_week = {"label": "Movies Watched", "value": total_week}
    average_week = {"label": "Average Rating", "value": average_week}
    fav_genre_week = {"label": "Go-to Genre", "value": fav_genre_week}
    fav_decade_week = {"label": "Golden Decade", "value": fav_decade_week}
    metrics_list_week = [total_movies_week, average_week, fav_genre_week, fav_decade_week]

    most_liked_disliked_week, most_liked_disliked_month, most_liked_disliked_year = get_liked_disliked_per_period(watched_movies)
    time_lag_week, time_lag_month, time_lag_year = get_time_lag_context_per_period(watched_movies)
    genre_category_week, genre_category_month, genre_category_year = get_genre_category_per_period(watched_movies)

    return {
        "watched_movies": watched_movies,

        "time_lag_week": time_lag_week,
        "time_lag_month": time_lag_month,
        "time_lag_year": time_lag_year,

        "genre_category_week": genre_category_week,
        "genre_category_month": genre_category_month,
        "genre_category_year": genre_category_year,

        "metrics_list_year": metrics_list_year,
        "metrics_list_month": metrics_list_month,
        "metrics_list_week": metrics_list_week,

        "most_liked_disliked_week": most_liked_disliked_week,
        "most_liked_disliked_month": most_liked_disliked_month,
        "most_liked_disliked_year": most_liked_disliked_year,
    }