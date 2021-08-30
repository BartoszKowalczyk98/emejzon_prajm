import io
import time
from threading import Thread

import boto3
from PIL import Image

from message_wrapper import receive_messages

sqs = boto3.resource('sqs', region_name='us-east-1')
s3 = boto3.resource('s3')

bucket_name = 'bk98flaskproject'
sqs_name = 'test_queue_psoir_239538'

queue = sqs.get_queue_by_name(QueueName=sqs_name)


def worker_thread():
    messages = []
    for message in receive_messages(queue=queue, max_number=1, wait_time=20):
        messages.append(message)

    for message in messages:
        s3_object = s3.meta.client.get_object(Bucket=bucket_name, Key=message.body)
        img = Image.open(io.BytesIO(s3_object['Body'].read()))

        filename_splitted = message.body.split('.')

        rotated = img.rotate(90)
        saved_img = io.BytesIO()
        # https://stackoverflow.com/questions/37048807/python-image-library-and-keyerror-jpg
        # w razie jeżeli dalej będą problemy z konwertowaniem to wyżej jest link do stacka
        ext = filename_splitted[1]
        rotated.save(saved_img, format='JPEG' if ext.lower() == 'jpg' else ext.upper())
        saved_img.seek(0)

        filename = filename_splitted[0] + '_rotated_.' + filename_splitted[1]

        s3.meta.client.put_object(Body=saved_img, Bucket=bucket_name, Key=filename)

        message.delete()
        print('done')


def main():
    while True:
        thread = Thread(target=worker_thread)
        thread.start()
        thread.join()
        time.sleep(5)


if __name__ == '__main__':
    main()
