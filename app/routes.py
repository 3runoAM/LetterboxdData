from flask import Blueprint, request, render_template, flash, redirect, url_for
from .data_processing import load_processed_diary, load_processed_ratings
from .file_processing import validate_files, save_files
from .graph_builder import plot_volume_por_periodo, plot_dia_semana, plot_evolucao_gosto, plot_taxa_rewatch, \
    plot_time_lag, get_max_streak, plot_distribuicao_notas, plot_decada_ouro

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def upload_files_route():
    return render_template("uploadFiles.html")

#-----------------------------------------------------------------------------------------------------------------------

@main.route("/saveFiles", methods=["POST"])
def save_files_route():
    files = request.files.getlist("files")
    valid, message = validate_files(files)

    if not valid:
        flash(message)
        return redirect(url_for("main.upload_files_route"))

    save_files(files)

    flash("Arquivos salvos com sucesso")
    return redirect(url_for("main.dashboard"))

#-----------------------------------------------------------------------------------------------------------------------

@main.route("/dashboard", methods=["GET"])
def dashboard():
    df_diary, df_streaks = load_processed_diary()
    df_rating = load_processed_ratings()

    dia_semana = plot_dia_semana(df_diary)
    evolucao_gosto = plot_evolucao_gosto(df_diary)
    taxa_rewatch = plot_taxa_rewatch(df_diary)
    time_lag = plot_time_lag(df_diary)
    distribuicao_notas = plot_distribuicao_notas(df_rating)
    decada_ouro = plot_decada_ouro(df_rating)

    return render_template("dashboard.html",
                           dia_semana=dia_semana,
                           evolucao_gosto=evolucao_gosto,
                           taxa_rewatch=taxa_rewatch,
                           time_lag=time_lag,
                           distribuicao_notas=distribuicao_notas,
                           decada_ouro=decada_ouro)