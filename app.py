import os
from io import BytesIO

import boto3
import requests
from flask import Flask, render_template, request, redirect, send_file
from werkzeug.wsgi import FileWrapper

from message_wrapper import send_messages
from presigned_url import create_presigned_url, create_presigned_post
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
        presigned_post = create_presigned_post(BUCKET, f.filename)
        requests.post(presigned_post['url'], presigned_post['fields'], files={'file': (path, open(path, "rb"))})
        return redirect("/")


@app.route('/rotate_images', methods=['POST'])
def rotate_image():
    if request.method == "POST":
        messages = []
        if request.form:
            for to_be_rotated in request.form:
                messages.append(pack_message("path", to_be_rotated, "line"))
            send_messages(queue, messages)

    return redirect("/")


@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        presigned_url = create_presigned_url(bucket_name=BUCKET, object_name=filename)
        output = requests.get(url=presigned_url)
        filename_splitted = filename.split('.')
        ext = filename_splitted[1]
        format = 'image/' + ext.lower()
        return send_file(
            BytesIO(output.content),
            mimetype=format,
            as_attachment=True,
            attachment_filename=filename)


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
    # app.run(host='0.0.0.0', port=80)
    app.run()
