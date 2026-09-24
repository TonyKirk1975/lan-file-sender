from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB

UPLOAD_FOLDER = Path(__file__).resolve().parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("files")
        uploaded = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                if not filename:
                    continue
                save_path = UPLOAD_FOLDER / filename
                if save_path.exists():
                    stem = save_path.stem
                    suffix = save_path.suffix
                    counter = 1
                    while save_path.exists():
                        save_path = UPLOAD_FOLDER / f"{stem}({counter}){suffix}"
                        counter += 1
                file.save(save_path)
                uploaded.append(filename)
        return render_template("index.html", uploaded=uploaded, files=sorted(p.name for p in UPLOAD_FOLDER.iterdir() if p.is_file()))

    files = sorted(p.name for p in UPLOAD_FOLDER.iterdir() if p.is_file())
    return render_template("index.html", uploaded=[], files=files)


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    file_path = UPLOAD_FOLDER / filename
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
