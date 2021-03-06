import io
import time
from threading import Thread

import boto3
from PIL import Image

from message_wrapper import receive_messages, delete_message

sqs = boto3.resource('sqs', region_name='us-east-1')
s3 = boto3.resource('s3')

bucket_name = 'bk98flaskproject'
sqs_name = 'test_queue_psoir_239538'

queue = sqs.get_queue_by_name(QueueName=sqs_name)


def message_operating_thread():
    # max wait_time żeby ciągnęło jak najmniej pieniędzy i żeby te do 5 wiadomości się mogło obsłużyć
    messages = receive_messages(queue=queue, max_number=5, wait_time=20)
    for message in messages:
        s3_object = s3.meta.client.get_object(Bucket=bucket_name, Key=message.body)
        img = Image.open(io.BytesIO(s3_object['Body'].read()))

        rotated_image = img.rotate(90)
        image_to_be_saved = io.BytesIO()

        # wyciągnięcie rozszerzenia z nazwy
        split = message.body.split('.')
        file_extension = split[1]

        # https://stackoverflow.com/questions/37048807/python-image-library-and-keyerror-jpg
        # w razie jeżeli dalej będą problemy z konwertowaniem to wyżej jest link do stacka
        rotated_image.save(image_to_be_saved, format='JPEG' if file_extension.lower() == 'jpg' else file_extension.upper())

        # powrót wskaźnika na początek do wrzucenia obiektu na s3
        image_to_be_saved.seek(0)

        filename = split[0] + '_rotated_.' + split[1]

        s3.meta.client.put_object(Body=image_to_be_saved, Bucket=bucket_name, Key=filename)

        delete_message(message)
        print('obsluzono plik ', filename, ' i usunieto message z sqs')


if __name__ == '__main__':
    while True:
        thread = Thread(target=message_operating_thread)
        thread.start()
        thread.join()
        time.sleep(5)
