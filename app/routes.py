from flask import Blueprint, request, render_template, flash, redirect, url_for

from app.services.context_engine import get_context
from app.services.etl_service import get_processed_data, transform_and_load
from app.services.graph_builder import plot_overview_wordcloud, plot_rewatch_rate, plot_movie_map
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

        return {"status": "success"}, 200
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return {"status": "error", "message": str(e)}, 500
# -----------------------------------------------------------------------------------------------------------------------

@main.route("/profile", methods=["GET"])
def profile_route():
    try:
        context = get_context()
        rewatch_rate_graph = plot_rewatch_rate()
        movie_map_graph = plot_movie_map()

        plot_overview_wordcloud()

        return render_template("profile.html", context=context, rewatch_rate=rewatch_rate_graph,
                               movie_map=movie_map_graph)

    except FileNotFoundError:
        flash("Data files not found. Please upload your data again.")
        return redirect(url_for("main.main_route"))
    except Exception as e:
        print(f"Data processing error: {e}")
        return redirect(url_for("main.main_route"))



# -----------------------------------------------------------------------------------------------------------------------

@main.route("/current-profile", methods=["GET"])
def current_profile():
    return render_template("currentProfile.html")


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/badges", methods=["GET"])
def badges_route():
    return render_template("badges.html")
