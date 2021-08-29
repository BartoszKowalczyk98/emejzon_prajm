import os
from flask import Flask, render_template, request, redirect, send_file
from s3_methods import list_files, download_file, upload_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
BUCKET = "bk98flaskproject"


#
# @app.route('/')
# def entry_point():
#     return 'Hello World!'


@app.route("/")
def storage():
    contents = list_files(BUCKET)
    return render_template('storage.html', contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))

        path = os.path.join(UPLOAD_FOLDER,f.filename)
        upload_file(path, BUCKET, f.filename, os.path.getsize(path))
        # upload_file(f.filename, BUCKET)

        return redirect("/")


@app.route('/invert_image/<filename>', methods=['POST'])
def invert_image(filename):
    if request.method == "POST":
        print(filename)
    return redirect("/")




@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        path = os.path.join(DOWNLOAD_FOLDER, filename)
        output = download_file(BUCKET, filename, path,1)

        return send_file(output, as_attachment=True)


def clean_up():
    # usuwanie z lokalnego folderu downloads
    download_folder_path = os.path.join(DOWNLOAD_FOLDER)
    for filename in os.listdir(download_folder_path):
        os.remove(os.path.join(DOWNLOAD_FOLDER, filename))

    # usuwanie plików z lokalnego folderu uploads
    upload_folder_path = os.path.join(UPLOAD_FOLDER)
    for filename in os.listdir(upload_folder_path):
        os.remove(os.path.join(UPLOAD_FOLDER, filename))


if __name__ == '__main__':
    clean_up()
    app.run(debug=True)

# todo wrzucanie plików do przeglądarki i to leci na s3 ma być zabezpieczony przed zapisem
#  i batchowe obrabianie danych z kolejki z uwzględnieniem jakiegoś systemu bezpieczeńswta
#  to będzie jako zalicznie do pokazania uruchomionej na infrastrukturze amazona
