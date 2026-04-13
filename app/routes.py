import os
import pandas
from flask import Blueprint, request, render_template, flash, redirect, url_for
from .context_engine import get_context
from .data_processing import process_diary, process_ratings, process_watched, get_processed_data
from .file_handler import validate_files, save_files, is_data_available, is_data_processed
from .graph_builder import plot_rewatch_rate, plot_overview_wordcloud
from .TMDB_Client import TMDBClient

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def main_route():
    if is_data_available() or is_data_processed():
        return redirect(url_for("main.perfil_route"))
    else:
        return render_template("upload.html")

# -----------------------------------------------------------------------------------------------------------------------

@main.route("/saveFiles", methods=["POST"])
def save_files_route():
    files = request.files.getlist("files")
    valid, message = validate_files(files)

    if not valid:
        flash(message)
        return redirect(url_for("main.main_route"))

    save_files(files)

    flash("Arquivos salvos com sucesso")
    return redirect(url_for("main.perfil_route"))

# -----------------------------------------------------------------------------------------------------------------------

@main.route("/perfil", methods=["GET"])
def perfil_route():
    try:
        # PROCESSAMENTO
        df_diary, df_rating, df_watched, movies = get_processed_data()

        # ENRIQUECIMENTO
        df_watched_enriched = None
        if not is_data_processed():
            client = TMDBClient(os.getenv("API_KEY"))
            enriched_data = client.fetch_movies_parallel(movies)
            df_enriched_data = pandas.DataFrame(enriched_data)
            df_watched_enriched = df_watched.merge(df_enriched_data, how="left", on=["Name", "Year"]).dropna(subset="Genres")
        else:
            df_watched_enriched = pandas.read_csv("data/dataFrames/df_watched_enriched.csv")

        # df_diary.to_csv("data/dataFrames/df_diary.csv", index=False)
        # df_rating.to_csv("data/dataFrames/df_rating.csv", index=False)
        # df_watched.to_csv("data/dataFrames/df_watched.csv", index=False)
        # df_watched_enriched.to_csv("data/dataFrames/df_watched_enriched.csv", index=False)

        # GERANDO CONTEXTO
        context = get_context(df_watched, df_diary, df_rating, df_watched_enriched)

        # GERAÇÃO DE GRÁFICOS E IMAGENS
        rewatch_rate = plot_rewatch_rate(df_diary)
        if not os.path.exists("app/static/images/overview_cloud.png"):
            plot_overview_wordcloud(df_watched_enriched)

    except FileNotFoundError:
        flash("Nenhum arquivo encontrado. Faça o upload dos arquivos necessários")
        return redirect(url_for("main.main_route"))
    except Exception as e:
        print(f"Erro ao processar os dados: {e.with_traceback(e.__traceback__)}")
        return redirect(url_for("main.main_route"))

    return render_template("profile.html",
                           context=context,
                           rewatch_rate=rewatch_rate)


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/perfilAtual", methods=["GET"])
def perfil_atual():
    return render_template("currentProfile.html")


# -----------------------------------------------------------------------------------------------------------------------

@main.route("/conquistas", methods=["GET"])
def conquistas_route():
    return render_template("badges.html")
