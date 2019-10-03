import boto3
from . import credentials


def aws_file_upload(file_path, file_name=None):
    if file_name is None:
        file_name = file_path

    s3_client = boto3.client('s3')
    s3_client.upload_file(file_path, credentials.AWS_UPLOAD_BUCKET, file_name)

    # url = "https://s3-fundoo-bucket.s3.us-east-2.amazonaws.com/" + "first-one"
