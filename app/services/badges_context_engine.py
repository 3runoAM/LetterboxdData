from datetime import timedelta

from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import coalesce

from app import data_base
from app.models import WatchLog, Movie


def get_rewatch_rate():
    result = data_base.session.query(
        coalesce(func.count(WatchLog.id), 0).label('total_diary'),
        coalesce(func.sum(case((WatchLog.is_rewatch == True, 1), else_=0)), 0).label('total_rewatches')
    ).first()

    total_diary = result.total_diary
    total_rewatches = result.total_rewatches

    rewatch_rate = (total_rewatches / total_diary) * 100 if total_diary > 0 else 0

    rewatch_badge_context = {
        "category_name": "Rewatch Behavior",
        "badges": [{
            "badge_name": "Resident",
            "is_active": False,
            "image_url": "/static/images/badges/resident.png",
            "description": f"Some people watch movies; you live in them. Your {rewatch_rate:.1f}% rewatch rate proves that a masterpiece only gets better with the 2nd viewing onwards"
        }, {
            "badge_name": "Curator",
            "is_active": False,
            "image_url": "/static/images/badges/curator.png",
            "description": f"You aren't afraid of new discoveries, but your {rewatch_rate:.1f}% rewatch rate shows that you never truly abandon your comfort films"
        }, {
            "badge_name": "Explorer",
            "is_active": False,
            "image_url": "/static/images/badges/explorer.png",
            "description": f"The world is too big to spend time watching the same thing twice, right? With {rewatch_rate:.1f}% rewatch rate, you prefer to keep moving forward and discover new stories"
        }, {
            "badge_name": "Trailblazer",
            "is_active": False,
            "image_url": "/static/images/badges/trailblazer.png",
            "description": f"\"Never look back\" is your motto for life. Your eyes are always on the horizon with {rewatch_rate:.1f}% rewatch rate"
        }]
    }

    if rewatch_rate >= 40:
        rewatch_badge_context.get("badges")[0]["is_active"] = True
    elif rewatch_rate >= 15:
        rewatch_badge_context.get("badges")[1]["is_active"] = True
    elif rewatch_rate >= 5:
        rewatch_badge_context.get("badges")[2]["is_active"] = True
    else:
        rewatch_badge_context.get("badges")[3]["is_active"] = True

    return rewatch_badge_context


def get_release_to_screen_interval():
    avg_lag_result = data_base.session.query(func.avg(WatchLog.time_lag)).scalar()

    avg_lag = float(avg_lag_result) if avg_lag_result is not None else 0.0

    time_lag_context = {
        "category_name": "Release-to-Screen Interval",
        "badges": [
            {
                "badge_name": "Historian",
                "is_active": False,
                "image_url": "/static/images/badges/historian.png",
                "description": f"Your time machine is permanently set to the past. With an average of {avg_lag:.1f} years between release dates and your screen, you cherish the timeless classics that shaped cinema"
            },
            {
                "badge_name": "Nostalgic",
                "is_active": False,
                "image_url": "/static/images/badges/nostalgic.png",
                "description": f"Your sweet spot is about {avg_lag:.1f} years back. You love revisiting or discovering those generation-defining gems that have aged like fine wine"
            },
            {
                "badge_name": "Modernist",
                "is_active": False,
                "image_url": "/static/images/badges/modernist.png",
                "description": f"You like giving movies some room to breathe. Your {avg_lag:.1f}-year average gap shows you catch up on great stories at your own pace, away from the immediate hype"
            },
            {
                "badge_name": "Trendsetter",
                "is_active": False,
                "image_url": "/static/images/badges/trendsetter.png",
                "description": f"You live in the absolute present. Your average gap is just {avg_lag:.1f} years—if a movie is any fresher, it would still be premiering in theaters"
            }
        ]
    }

    if avg_lag >= 30:
        time_lag_context["badges"][0]["is_active"] = True
    elif avg_lag >= 15:
        time_lag_context["badges"][1]["is_active"] = True
    elif avg_lag >= 5:
        time_lag_context["badges"][2]["is_active"] = True
    else:
        time_lag_context["badges"][3]["is_active"] = True

    return time_lag_context


def get_cinema_trait():
    movies = (data_base.session.query(WatchLog)
              .options(joinedload(WatchLog.movie).selectinload(Movie.genres))
              .order_by(WatchLog.watched_date.desc())
              .all())

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
        rating = movie.rating
        for genre in movie.movie.genres:
            genre_name = genre.name
            for category, genres in genre_category_mapping.items():
                if genre_name in genres:
                    graph_points[category] += rating
                    points += rating
                    break

    categories = list(genre_category_mapping.keys())
    values = [round((graph_points[category] / points) * 100, 1) for category in
              categories] if points > 0 else [0] * len(categories)

    max_value_category = categories[values.index(max(values))] if points > 0 else None

    cinema_trait_context = {
        "category_name": "Cinema Trait",
        "badges": [{
            "badge_name": "Adrenaline",
            "is_active": False,
            "image_url": "/static/images/badges/adrenaline.png",
            "description": "Your time was dominated by the Adrenaline trait: you thrived on high-octane action, fast-paced plots, and heart-pounding blockbusters that kept you on the edge of your seat"
        }, {
            "badge_name": "Shiver",
            "is_active": False,
            "image_url": "/static/images/badges/shiver.png",
            "description": "Your time was dominated by the Shiver trait: you had a strong craving for the darker side of cinema, preferring tense thrillers, eerie mysteries, and horror stories that tested your nerves"
        }, {
            "badge_name": "Brain",
            "is_active": False,
            "image_url": "/static/images/badges/brain.png",
            "description": "Your time was dominated by the Brain trait: you looked for psychological depth, mind-bending sci-fi, and complex narratives that left you thinking long after the credits rolled"
        }, {
            "badge_name": "Emotion",
            "is_active": False,
            "image_url": "/static/images/badges/emotion.png",
            "description": "Your time was dominated by the Emotion trait: you were drawn to powerful dramas, sweeping romances, and deeply moving stories crafted to touch your heart or make you shed a tear"
        }, {
            "badge_name": "Escapism",
            "is_active": False,
            "image_url": "/static/images/badges/escapism.png",
            "description": "Your time was dominated by the Escapism trait: you loved lighthearted comedies, animated wonders, and pure fantasy—the perfect cinematic escape to unwind and unplug from reality"
        }]
    }

    if max_value_category == 'Adrenaline':
        cinema_trait_context["badges"][0]["is_active"] = True
    elif max_value_category == 'Shiver':
        cinema_trait_context["badges"][1]["is_active"] = True
    elif max_value_category == 'Brain':
        cinema_trait_context["badges"][2]["is_active"] = True
    elif max_value_category == 'Emotion':
        cinema_trait_context["badges"][3]["is_active"] = True
    elif max_value_category == 'Escapism':
        cinema_trait_context["badges"][4]["is_active"] = True

    return cinema_trait_context


def get_weekly_routine():
    day_counts = (
        data_base.session.query(WatchLog.day_of_week, func.count(WatchLog.id).label('total_watches')).group_by(
            WatchLog.day_of_week).all())

    weekend_days = {'Friday', 'Saturday', 'Sunday'}
    weekend_count = 0
    routine_count = 0

    for row in day_counts:
        day = row.day_of_week
        count = row.total_watches
        if day in weekend_days:
            weekend_count += count
        else:
            routine_count += count

    weekly_routine_context = {
        "category_name": "Weekly Routine",
        "badges": [
            {
                "badge_name": "Weekend Warrior",
                "is_active": False,
                "image_url": "/static/images/badges/weekend.png",
                "description": "Cinema is your ultimate weekend escape. With your watch history heavily concentrated from Friday to Sunday, you treat movies as the perfect reward to unwind and power down"
            },
            {
                "badge_name": "Routine Cinephile",
                "is_active": False,
                "image_url": "/static/images/badges/routine.png",
                "description": "Movies are seamlessly woven into your daily rhythm. With a steady distribution of views from Monday to Thursday, cinema is part of your regular routine, not just a weekend luxury"
            }
        ]
    }

    if weekend_count > routine_count:
        weekly_routine_context["badges"][0]["is_active"] = True
    else:
        weekly_routine_context["badges"][1]["is_active"] = True

    return weekly_routine_context


def get_viewing_streak():
    watched_dates = (data_base.session.query(func.date(WatchLog.watched_date))
                     .distinct()
                     .order_by(func.date(WatchLog.watched_date).asc())
                     .all())

    max_streak = 0
    current_streak = 0
    previous_date = None
    for row in watched_dates:
        current_date = row[0]

        if previous_date is None:
            current_streak = 1
        elif current_date == previous_date + timedelta(days=1):
            current_streak += 1
        elif current_date > previous_date + timedelta(days=1):
            if current_streak > max_streak:
                max_streak = current_streak
            current_streak = 1

        previous_date = current_date

    if current_streak > max_streak:
        max_streak = current_streak

    if max_streak < 2:
        max_streak = 0

    viewing_streak_context = {
        "category_name": "Viewing Streak",
        "badges": [
            {
                "badge_name": "Marathoner",
                "is_active": False,
                "image_url": "/static/images/badges/marathoner.png",
                "description": f"Once you press play, nothing can stop you. Your impressive {max_streak}-day consecutive streak proves you don't just watch movies—you live in an endless cinematic loop."
            },
            {
                "badge_name": "Binge Watcher",
                "is_active": False,
                "image_url": "/static/images/badges/binge.png",
                "description": f"You know exactly how to turn a regular week into a dedicated film festival. With a solid {max_streak}-day streak, you hit the perfect rhythm of non-stop entertainment."
            },
            {
                "badge_name": "Casual Streaker",
                "is_active": False,
                "image_url": "/static/images/badges/casual.png",
                "description": f"A quick weekend burst or back-to-back movie nights are your sweet spot. Your {max_streak}-day streak shows you love keeping the momentum going without burning out."
            },
            {
                "badge_name": "Paced Viewer",
                "is_active": False,
                "image_url": "/static/images/badges/paced.png",
                "description": "You prefer to let every single film breathe. Without keeping daily streaks, you treat movies as standalone events, giving your mind plenty of time to process each story."
            }
        ]
    }

    if max_streak >= 7:
        viewing_streak_context["badges"][0]["is_active"] = True
    elif max_streak >= 4:
        viewing_streak_context["badges"][1]["is_active"] = True
    elif max_streak >= 2:
        viewing_streak_context["badges"][2]["is_active"] = True
    else:
        viewing_streak_context["badges"][3]["is_active"] = True

    return viewing_streak_context


def get_rating_pattern():
    avg_rating_result = data_base.session.query(func.avg(WatchLog.rating)).scalar()
    avg_rating = float(avg_rating_result) if avg_rating_result is not None else 0.0

    rating_pattern_context = {
        "category_name": "Rating Pattern",
        "badges": [
            {
                "badge_name": "Cinematic Enthusiast",
                "is_active": False,
                "image_url": "/static/images/badges/enthusiast.png",
                "description": f"You find magic in almost everything you watch. With a generous average rating of {avg_rating:.1f} stars, you celebrate the joy of cinema and love giving films the praise they deserve."
            },
            {
                "badge_name": "Balanced Juror",
                "is_active": False,
                "image_url": "/static/images/badges/juror.png",
                "description": f"You treat your ratings with absolute fairness. Your {avg_rating:.1f}-star average shows a perfectly balanced scale, separating the true masterpieces from the average crowd."
            },
            {
                "badge_name": "Strict Connoisseur",
                "is_active": False,
                "image_url": "/static/images/badges/connoisseur.png",
                "description": f"You hold cinema to an exceptionally high standard. An average rating of {avg_rating:.1f} stars means a movie truly has to earn your respect to get a passing grade."
            },
            {
                "badge_name": "Brutal Executioner",
                "is_active": False,
                "image_url": "/static/images/badges/executioner.png",
                "description": f"To put it bluntly: you are incredibly hard to please. Your ruthless {avg_rating:.1f}-star average proves that most films simply crumble under your razor-sharp critical gaze."
            }
        ]
    }

    if avg_rating >= 4.0:
        rating_pattern_context["badges"][0]["is_active"] = True
    elif avg_rating >= 3.0:
        rating_pattern_context["badges"][1]["is_active"] = True
    elif avg_rating >= 2.0:
        rating_pattern_context["badges"][2]["is_active"] = True
    else:
        rating_pattern_context["badges"][3]["is_active"] = True

    return rating_pattern_context


def get_decade_preference():
    era_counts = (data_base.session.query(
        Movie.release_year,
        func.count(WatchLog.id).label('count')
    )
                  .join(WatchLog.movie)
                  .group_by(Movie.release_year)
                  .all())

    modern_count = 0  # 2010 em diante
    turn_century_count = 0  # 1990 até 2009
    retro_count = 0  # 1970 até 1989
    classic_count = 0  # Antes de 1970

    for row in era_counts:
        year = row.release_year
        count = row.count

        if year >= 2010:
            modern_count += count
        elif year >= 1990:
            turn_century_count += count
        elif year >= 1970:
            retro_count += count
        else:
            classic_count += count

    decade_preference_context = {
        "category_name": "Decade Preference",
        "badges": [
            {
                "badge_name": "Contemporary Fan",
                "is_active": False,
                "image_url": "/static/images/badges/contemporary.png",
                "description": "You live on the cutting edge of cinema. Your history is dominated by the 2010s and 2020s, showcasing your preference for state-of-the-art visuals and current storytelling."
            },
            {
                "badge_name": "Millennial Nostalgic",
                "is_active": False,
                "image_url": "/static/images/badges/millennial.png",
                "description": "Your heart belongs to the era of indie revolutions and peak physical media. Your focus on the 90s and 2000s shows you cherish the generation-defining stories you grew up with."
            },
            {
                "badge_name": "Retro Aficionado",
                "is_active": False,
                "image_url": "/static/images/badges/retro.png",
                "description": "Neon lights, synth pads, and gritty auteur cinema drive your taste. Your heavy focus on the 70s and 80s highlights your deep appreciation for the boldest decades in film history."
            },
            {
                "badge_name": "Golden Age Scholar",
                "is_active": False,
                "image_url": "/static/images/badges/golden_age.png",
                "description": "You worship the foundational pillars of cinema. By dedicating your time mostly to pre-1970 classics, you show a profound respect for black-and-white masterpieces and silver screen icons."
            }
        ]
    }

    max_count = max(modern_count, turn_century_count, retro_count, classic_count)

    if max_count == modern_count:
        decade_preference_context["badges"][0]["is_active"] = True
    elif max_count == turn_century_count:
        decade_preference_context["badges"][1]["is_active"] = True
    elif max_count == retro_count:
        decade_preference_context["badges"][2]["is_active"] = True
    else:
        decade_preference_context["badges"][3]["is_active"] = True

    return decade_preference_context


def get_badges_context():
    rewatch_badge = get_rewatch_rate()
    release_to_screen_badge = get_release_to_screen_interval()
    cinema_trait_badge = get_cinema_trait()
    weekly_routine_badge = get_weekly_routine()
    viewing_streak_badge = get_viewing_streak()
    rating_pattern_badge = get_rating_pattern()
    golden_decade_badge = get_decade_preference()

    badges_context = [rewatch_badge, release_to_screen_badge, cinema_trait_badge, weekly_routine_badge,
                      viewing_streak_badge, rating_pattern_badge, golden_decade_badge]

    return badges_context
