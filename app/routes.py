from flask import Blueprint, request, render_template, flash, redirect, url_for
from .file_processing import validate_files, save_files

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def upload_files_route():
    return render_template("uploadFiles.html")

#-----------------------------------------------------------------------------------------------------------------------

@main.route("/saveFiles", methods=["POST"])
def save_files_route():
    print("| Recebendo arquivos...")
    files = request.files.getlist("files")

    print("| Validando arquivos...")
    valid, message = validate_files(files)

    if not valid:
        print("| ERRO: " + message)
        flash(message)
        return redirect(url_for("main.upload_files_route"))

    print("| Salvando arquivos...")
    save_files(files)

    flash("Arquivos salvos com sucesso")
    return redirect(url_for("main.dashboard"))

#-----------------------------------------------------------------------------------------------------------------------

@main.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")