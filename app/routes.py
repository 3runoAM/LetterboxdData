import os
import pandas
from flask import Blueprint, request, render_template, flash, redirect, url_for
from .context_engine import get_context
from .data_processing import process_diary, process_ratings, process_watched, get_processed_data
from .file_handler import validate_files, save_files, is_data_available, is_data_processed
from .graph_builder import plot_rewatch_rate, plot_overview_wordcloud, plot_movie_map
from .TMDB_Client import TMDBClient

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def main_route():
    if not is_data_available() or not is_data_processed():
        return render_template("upload.html")
    else:
        return redirect(url_for("main.profile_route"))

# -----------------------------------------------------------------------------------------------------------------------

@main.route("/saveFiles", methods=["POST"])
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

        client = TMDBClient(os.getenv("API_KEY"))
        enriched_data = client.fetch_movies_parallel(movies)

        df_enriched = pandas.DataFrame(enriched_data)
        df_watched_enriched = df_watched.merge(df_enriched, how="left", on=["Name", "Year"]).dropna(subset="Genres")

        df_diary.to_csv("data/dataFrames/df_diary.csv", index=False)
        df_rating.to_csv("data/dataFrames/df_rating.csv", index=False)
        df_watched.to_csv("data/dataFrames/df_watched.csv", index=False)
        df_watched_enriched.to_csv("data/dataFrames/df_watched_enriched.csv", index=False)

        plot_overview_wordcloud(df_watched_enriched)

        return {"status": "success"}, 200
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return {"status": "error", "message": str(e)}, 500
# -----------------------------------------------------------------------------------------------------------------------

@main.route("/perfil", methods=["GET"])
def profile_route():
    try:
        if not is_data_processed():
            return redirect(url_for("main.main_route"))

        df_diary = pandas.read_csv("data/dataFrames/df_diary.csv", parse_dates=["Date", "Watched Date"])
        df_rating = pandas.read_csv("data/dataFrames/df_rating.csv", parse_dates=["Date"])
        df_watched = pandas.read_csv("data/dataFrames/df_watched.csv", parse_dates=["Date"])
        df_watched_enriched = pandas.read_csv("data/dataFrames/df_watched_enriched.csv", parse_dates=["Date"])

        context = get_context(df_watched, df_diary, df_rating, df_watched_enriched)
        rewatch_rate_graph = plot_rewatch_rate(df_diary)
        movie_map_graph = plot_movie_map(df_watched_enriched)

        return render_template("profile.html", context=context, rewatch_rate=rewatch_rate_graph,
                               movie_map=movie_map_graph)

    except FileNotFoundError:
        flash("Data files not found. Please upload your data again.")
        return redirect(url_for("main.main_route"))
    except Exception as e:
        print(f"Data processing error: {e}")
        return redirect(url_for("main.main_route"))



# -----------------------------------------------------------------------------------------------------------------------

@main.route("/perfilAtual", methods=["GET"])
def current_profile():
    return render_template("currentProfile.html")


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/conquistas", methods=["GET"])
def badges_route():
    return render_template("badges.html")
