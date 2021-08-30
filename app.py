import os

import boto3
from flask import Flask, render_template, request, redirect, send_file

from message_wrapper import send_messages
from s3_methods import list_files, download_file, upload_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"
BUCKET = "bk98flaskproject"
sqs = boto3.resource('sqs', region_name='us-east-1')
sqs_name = 'test_queue_psoir_239538'
queue = sqs.get_queue_by_name(QueueName=sqs_name)


@app.route("/")
def storage():
    contents = list_files(BUCKET)
    return render_template('storage.html', contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))

        path = os.path.join(UPLOAD_FOLDER, f.filename)
        upload_file(path, BUCKET, f.filename, os.path.getsize(path))
        # upload_file(f.filename, BUCKET)

        return redirect("/")


@app.route('/invert_images', methods=['POST'])
def invert_image():
    if request.method == "POST":
        messages = []
        for to_be_inverted in request.form:
            messages.append(pack_message("path", to_be_inverted, "line"))
        send_messages(queue, messages)

    return redirect("/")


@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        path = os.path.join(DOWNLOAD_FOLDER, filename)
        output = download_file(BUCKET, filename, path, 1)

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


def pack_message(msg_path, msg_body, msg_line):
    return {
        'body': msg_body,
        'attributes': {
            'path': {'StringValue': msg_path, 'DataType': 'String'},
            'line': {'StringValue': str(msg_line), 'DataType': 'String'}
        }
    }


if __name__ == '__main__':
    clean_up()
    app.run(debug=True)

# todo wrzucanie plików do przeglądarki i to leci na s3 ma być zabezpieczony przed zapisem
#  i batchowe obrabianie danych z kolejki z uwzględnieniem jakiegoś systemu bezpieczeńswta
#  to będzie jako zalicznie do pokazania uruchomionej na infrastrukturze amazona
