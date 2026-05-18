from datetime import timedelta

from sqlalchemy import func, extract, case

from app.data_base import data_base
from app.models import Movie, Genre, Director, WatchLog


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


def get_context():
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
