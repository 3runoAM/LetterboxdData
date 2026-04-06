import os

import pandas
from flask import Blueprint, request, render_template, flash, redirect, url_for

from . import TMDB_Client
from .feature_engine import get_context
from .data_processing import process_diary, process_ratings, process_watched, get_processed_data
from .file_handler import validate_files, save_files, is_data_available
from .graph_builder import plot_favorite_day, plot_likeness_series, plot_rewatch_rate, \
    plot_time_lag, plot_rating_distribution, plot_favorite_decade
from .TMDB_Client import TMDBClient

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def main_route():
    if is_data_available():
        return redirect(url_for("main.perfil_route"))
    else:
        return render_template("upload.html")

#-----------------------------------------------------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------------------------------------------------

@main.route("/perfil", methods=["GET"])
def perfil_route():
    try:
        # PROCESSAMENTO E ENRIQUECIMENTO DOS DADOS
        df_diary, df_rating, df_watched, movies = get_processed_data()

        client = TMDBClient(os.getenv("API_KEY"))

        enrich_data = client.fetch_movies_parallel(movies)
        df_enrich_data = pandas.DataFrame(enrich_data)

        df_watched_enriched = df_watched.merge(df_enrich_data, how="left", on=["Name", "Year"]).dropna(subset="Genres")
        # df_watched_enriched.to_csv("app/static/df_watched.csv", index=False)

        # GERANDO INSIGHTS
        context = get_context(df_watched, df_diary, df_rating, df_watched_enriched)

        # GERAÇÃO DOS GRÁFICOS COM PLOTLY
        favorite_day = plot_favorite_day(df_diary)
        likeness_series = plot_likeness_series(df_diary)
        rewatch_rate = plot_rewatch_rate(df_diary)
        time_lag = plot_time_lag(df_diary)
        rating_distribution = plot_rating_distribution(df_rating)
        favorite_decade = plot_favorite_decade(df_rating)

    except FileNotFoundError:
        flash("Nenhum arquivo encontrado. Faça o upload dos arquivos necessários")
        return redirect(url_for("main.main_route"))
    except Exception as e:
        print(f"Erro ao processar os dados: {e.with_traceback(e.__traceback__)}")
        return redirect(url_for("main.main_route"))

    return render_template("perfil.html",
                           context=context,
                           favorite_day=favorite_day,
                           likeness_series=likeness_series,
                           rewatch_rate=rewatch_rate,
                           time_lag=time_lag,
                           rating_distribution=rating_distribution,
                           favorite_decade=favorite_decade)

#-----------------------------------------------------------------------------------------------------------------------

@main.route("/perfilAtual", methods=["GET"])
def perfil_atual():
    return render_template("perfilAtual.html")