import time
from threading import Thread
from PIL import Image, ImageOps
import boto3
import io

sqs = boto3.resource('sqs', region_name='us-east-1')
s3 = boto3.resource('s3')

bucket_name = 'bk98flaskproject'
sqs_name = 'test_queue_psoir_239538'


def worker_thread():
    queue = sqs.get_queue_by_name(QueueName=sqs_name)
    messages = []
    for message in queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=20):
        messages.append(message)

    for item in messages:  # should be only one always
        s3_object = s3.meta.client.get_object(Bucket=bucket_name, Key=item.body)
        img = Image.open(io.BytesIO(s3_object['Body'].read()))

        filename_splitted = item.body.split('.')

        inverted = ImageOps.invert(img.convert('RGB'))
        saved_img = io.BytesIO()
        ext = filename_splitted[1]
        inverted.save(saved_img, format='JPEG' if ext.lower() == 'jpg' else ext.upper())
        saved_img.seek(0)

        filename = filename_splitted[0] + '_inverted.' + filename_splitted[1]

        s3.meta.client.put_object(Body=saved_img, Bucket=bucket_name, Key=filename)

        item.delete()
        print('done')


def main():
    while True:
        thread = Thread(target=worker_thread)
        thread.start()
        thread.join()
        time.sleep(5)


if __name__ == '__main__':
    main()
