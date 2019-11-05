import boto3


from fundoo.fundoo.settings import AWS_STORAGE_BUCKET_NAME


def aws_file_upload(file_path, file_name=None):
    if file_name is None:
        file_name = file_path
    s3_client = boto3.client('s3')
    s3_client.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, file_name)
