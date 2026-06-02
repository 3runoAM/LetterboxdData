import calendar
from collections import Counter, defaultdict
from datetime import timedelta, date
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload

from app.data_base import data_base
from app.models import Movie, Genre, Director, WatchLog


# PROFILE CONTEXT ------------------------------------------------------------------------------------------------------
def get_total_movies():
    return data_base.session.query(Movie).count() or None

def get_average_rating():
    return round(data_base.session.query(func.avg(WatchLog.rating)).scalar(), 1) or None

def get_favorite_day():
    result = (data_base.session.query(
        WatchLog.day_of_week.label("day_name"),
        func.count(WatchLog.day_of_week).label("day_count")
    ).group_by(WatchLog.day_of_week)
              .order_by(func.count(WatchLog.day_of_week).desc())
              .first())

    return result.day_name or None

def get_favorite_decade():
    result = (data_base.session.query(
        Movie.decade.label("decade"),
        func.avg(WatchLog.rating).label("average_rating"),
        func.count(WatchLog.id).label("log_count")
    ).join(WatchLog, Movie.id == WatchLog.movie_id)
              .group_by(Movie.decade)
              .having(func.count(WatchLog.id) >= 5)
              .order_by(func.avg(WatchLog.rating).desc())
              .first())

    return result.decade or None

def get_favorite_genre():
    result = (data_base.session.query(
        Genre.name.label('genre_name'),
        func.avg(WatchLog.rating).label('average_rating'),
        func.count(WatchLog.id).label('watch_count')
    ).select_from(WatchLog)
              .join(Movie, WatchLog.movie_id == Movie.id)
              .join(Movie.genres)
              .group_by(Genre.name)
              .having(func.count(WatchLog.id) >= 5)
              .order_by(
        func.count(WatchLog.id).desc(),
        func.avg(WatchLog.rating).desc())
              .first())

    return result.genre_name or None

def get_most_frequent_director():
    result = (data_base.session.query(
        Director.name.label("director_name"),
        func.count(WatchLog.id).label("watch_count"),
        func.avg(WatchLog.rating).label('average_rating')
    ).select_from(WatchLog)
              .join(Movie, WatchLog.movie_id == Movie.id)
              .join(Movie.directors)
              .group_by(Director.name)
              .order_by(
        func.count(WatchLog.id).desc(),
        func.avg(WatchLog.rating).desc())
              .first())

    return result.director_name or None

def get_rewatch_context():
    result = data_base.session.query(
        func.count(WatchLog.id).label('total_diary'),
        func.sum(case((WatchLog.is_rewatch == True, 1), else_=0)).label('total_rewatches')
    ).first()

    total_diary = result.total_diary or 0
    total_rewatches = result.total_rewatches or 0

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
    result = (data_base.session.query(
        Movie.title,
        Movie.poster_url,
        Movie.release_year,
        WatchLog.rating
    ).join(WatchLog, Movie.id == WatchLog.movie_id)
              .filter(WatchLog.is_rewatch == True)
              .order_by(WatchLog.watched_date.desc())
              .all())

    rewatched_movies = []
    for movie in result:
        rewatched_movies.append({
            "name": movie.title,
            "poster": movie.poster_url,
            "year": movie.release_year,
            "rating": movie.rating
        })

    return {
        "rewatch_profile": rewatch_profile,
        "rewatch_description": rewatch_description,
        "rewatched_movies": rewatched_movies
    }

def get_streak_context():
    result = (data_base.session.query(WatchLog.watched_date.label("watch_date"))
              .distinct()
              .order_by(WatchLog.watched_date.asc())
              .all())

    if not result:
        return {"days": 0, "start": None, "end": None, "movies": None}

    all_dates = [date.watch_date for date in result]
    longest_streak = []
    current_streak = [all_dates[0]]

    for i in range(1, len(all_dates)):
        if all_dates[i] == all_dates[i - 1] + timedelta(days=1):
            current_streak.append(all_dates[i])
        else:
            if len(current_streak) > len(longest_streak):
                longest_streak = current_streak
            current_streak = [all_dates[i]]

    if len(current_streak) > len(longest_streak):
        longest_streak = current_streak

    max_days = len(longest_streak)
    start_date = longest_streak[0]
    end_date = longest_streak[-1]

    streak_movies = []
    if max_days > 1:
        movies_on_streak = (data_base.session.query(
            Movie.title,
            Movie.release_year,
            Movie.poster_url,
            WatchLog.rating
        ).join(WatchLog, Movie.id == WatchLog.movie_id)
                            .filter(WatchLog.watched_date >= start_date, WatchLog.watched_date <= end_date)
                            .order_by(WatchLog.rating.desc())
                            .all())

        for movie in movies_on_streak:
            streak_movies.append({
                "name": movie.title,
                "year": movie.release_year,
                "poster": movie.poster_url,
                "rating": movie.rating
            })

    def format_date(date):
        return date.strftime("%B %d, %Y")

    return {
        "days": max_days,
        "start": format_date(start_date),
        "end": format_date(end_date),
        "movies": streak_movies,
    }

def get_movie_moment_context():
    total_movies = data_base.session.query(func.count(Movie.id)).scalar()

    favorite_day_result = (data_base.session.query(
        WatchLog.day_of_week.label("day_of_week"),
        func.count(WatchLog.id).label("day_count")
    )
                           .group_by(WatchLog.day_of_week)
                           .order_by(func.count(WatchLog.id).desc())
                           .first())

    favorite_day = favorite_day_result.day_of_week
    total_from_favorite_day = favorite_day_result.day_count

    top_genre = (data_base.session.query(Genre.name.label("genre"))
                 .select_from(WatchLog)
                 .join(Movie)
                 .join(Movie.genres)
                 .filter(WatchLog.day_of_week == favorite_day)
                 .group_by(Genre.name)
                 .order_by(func.count(WatchLog.id).desc())
                 .first())
    top_genre = top_genre.genre

    top_decade = (data_base.session.query(
        Movie.decade.label("decade"),
        func.avg(WatchLog.rating).label("average_rating"),
        func.count(WatchLog.id).label("log_count")
    ).select_from(WatchLog)
                  .join(Movie)
                  .join(Movie.genres)
                  .filter(WatchLog.day_of_week == favorite_day, Genre.name == top_genre)
                  .group_by(Movie.decade)
                  .order_by(func.avg(WatchLog.rating).desc())
                  .first())

    top_decade = top_decade.decade
    movie_percentage = (total_from_favorite_day / total_movies) * 100

    return {
        "favorite_day": favorite_day.capitalize(),
        "favorite_genre": top_genre.capitalize(),
        "favorite_decade": top_decade,
        "movie_percentage": round(movie_percentage, 1),
    }

def get_profile_context():
    total_movies = {"label": "Movies Watched", "value": get_total_movies()}
    favorite_day = {"label": "Cinema Day", "value": get_favorite_day()}
    favorite_decade = {"label": "Golden Decade", "value": get_favorite_decade()}
    average_rating = {"label": "Average Rating", "value": get_average_rating()}
    favorite_genre = {"label": "Go-to Genre", "value": get_favorite_genre()}
    favorite_director = {"label": "Resident Director", "value": get_most_frequent_director()}

    metric_list = [total_movies, favorite_day, favorite_decade, average_rating, favorite_genre, favorite_director]

    streak_context = get_streak_context()
    rewatch_context = get_rewatch_context()
    movie_context = get_movie_moment_context()

    return {
        "metric_list": metric_list,
        "streak_context": streak_context,
        "rewatch_context": rewatch_context,
        "movie_context": movie_context,
    }

# CURRENT PROFILE CONTEXT ----------------------------------------------------------------------------------------------

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
            "genres": [genre.name for genre in watch_log.movie.genres]
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

        decades = [(movie.get("year") // 10) * 10 for movie in movies]
        decade_count = Counter(decades)

        return decade_count.most_common(1)[0][0]

    fav_decade_week = calculate_favorite_decade(watched_movies.get("watched_this_week"))
    fav_decade_month = calculate_favorite_decade(watched_movies.get("watched_this_month"))
    fav_decade_year = calculate_favorite_decade(watched_movies.get("watched_this_year"))

    return fav_decade_week, fav_decade_month, fav_decade_year

def get_liked_disliked_per_period(watched_movies):
    def calculate_liked_disliked(movies):
        if not movies:
            return None

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

# def a():
#     return None

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

    return {
        "watched_movies": watched_movies,

        "metrics_list_year": metrics_list_year,
        "metrics_list_month": metrics_list_month,
        "metrics_list_week": metrics_list_week,

        "most_liked_disliked_week": most_liked_disliked_week,
        "most_liked_disliked_month": most_liked_disliked_month,
        "most_liked_disliked_year": most_liked_disliked_year,
    }
