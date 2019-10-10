import boto3

import fundoo


# print(settings.MEDIA_ROOT)
def aws_file_upload(file_path, file_name=None):
    if file_name is None:
        file_name = file_path
    s3_client = boto3.client('s3')
    s3_client.upload_file(file_path, fundoo.settings.AWS_UPLOAD_BUCKET, file_name)

