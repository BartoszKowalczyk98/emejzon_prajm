import os
from flask import Flask, render_template, request, redirect, send_file
from s3_methods import list_files, download_file, upload_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "bk98flaskproject"


#
# @app.route('/')
# def entry_point():
#     return 'Hello World!'


@app.route("/")
def storage():
    contents = list_files("bk98flaskproject")
    return render_template('storage.html', contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        upload_file(f"uploads/{f.filename}", BUCKET)
        # upload_file(f.filename, BUCKET)

        return redirect("/")


@app.route('/invert_image/<filename>', methods=['POST'])
def invert_image(filename):
    if request.method == "POST":
        print(filename)
    return redirect("/")



@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    print(filename)
    if request.method == 'GET':
        output = download_file(filename, BUCKET)

        return send_file(output, as_attachment=True)




if __name__ == '__main__':
    app.run(debug=True)

# todo wrzucanie plików do przeglądarki i to leci na s3 ma być zabezpieczony przed zapisem
#  i batchowe obrabianie danych z kolejki z uwzględnieniem jakiegoś systemu bezpieczeńswta
#  to będzie jako zalicznie do pokazania uruchomionej na infrastrukturze amazona
