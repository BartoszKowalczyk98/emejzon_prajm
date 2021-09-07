import boto3

s3 = boto3.resource('s3')


def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    list_of_s3_objects = s3.list_objects(Bucket=bucket)['Contents']
    if list_of_s3_objects:
        for item in list_of_s3_objects:
            contents.append(item)
    return contents
