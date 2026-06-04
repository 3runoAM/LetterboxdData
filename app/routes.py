from flask import Blueprint, request, render_template, flash, redirect, url_for

from app.services.context_engine import get_profile_context, get_current_profile_context
from app.services.etl_service import get_processed_data, transform_and_load
from app.services.graph_builder import plot_overview_wordcloud, plot_rewatch_rate, plot_movie_map, \
    plot_time_lag_per_period, plot_points_graph_per_period
from app.utils.file_handler import validate_files, save_files, is_data_available

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def main_route():
    if not is_data_available():
        return render_template("upload.html")
    else:
        return redirect(url_for("main.profile_route"))


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/save-files", methods=["POST"])
def save_files_route():
    files = request.files.getlist("files")
    valid, message = validate_files(files)

    if not valid:
        flash(message)
        return redirect(url_for("main.main_route"))

    save_files(files)
    return render_template("loading.html")


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/api/process-data", methods=["POST"])
def process_data():
    try:
        df_diary, df_rating, df_watched, movies = get_processed_data()

        transform_and_load(movies, df_watched, df_diary)

        plot_overview_wordcloud()

        return {"status": "success"}, 200
    except Exception as e:
        print(f"Data processing error: {e}")
        return {"status": "error", "message": str(e)}, 500


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/profile", methods=["GET"])
def profile_route():
    try:
        context = get_profile_context()

        rewatch_rate_graph = plot_rewatch_rate()

        movie_map_graph = plot_movie_map()

        return render_template("profile.html", context=context, rewatch_rate=rewatch_rate_graph,
                               movie_map=movie_map_graph)
    except Exception as e:
        print(f"Data processing error: {e}")
        return redirect(url_for("main.main_route"))


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/current-profile", methods=["GET"])
def current_profile():
    try:
        context = get_current_profile_context()

        time_lag_graphs = plot_time_lag_per_period(context.get("watched_movies"),
                                                   [context.get("time_lag_week").get("time_lag_average"),
                                                    context.get("time_lag_month").get("time_lag_average"),
                                                    context.get("time_lag_year").get("time_lag_average")])

        genre_category_graphs = plot_points_graph_per_period([context.get("genre_category_week"),
                                                              context.get("genre_category_month"),
                                                              context.get("genre_category_year")])
    except Exception as e:
        print(f"Data processing error: {e}")
        return redirect(url_for("main.main_route"))

    return render_template("currentProfile.html",
                           context=context, time_lag_graphs=time_lag_graphs, genre_category_graphs=genre_category_graphs, )


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/badges", methods=["GET"])
def badges_route():
    return render_template("badges.html")
