import boto3
import botocore
from botocore.client import Config
import json


class S3_integration:

    ACCESS_KEY_ID = '--here is your access key from S3--'
    ACCESS_SECRET_KEY = '--access secret key--'
    BUCKET_NAME = '--bucket name--'
    s3 = boto3.resource('s3',
                        aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=ACCESS_SECRET_KEY,
                        config=Config(signature_version='s3v4'))

    def put(self, key, data_dict):  # data as a dictionary
        data = json.dumps(data_dict)
        try:  # too many put requests, changing it back to local files
            # s3_object = self.s3.Object(self.BUCKET_NAME, key)
            # s3_object.put(Body=data)
            if key == 'dict_storage':
                file_path = 'Storage/dict_storage.txt'
            elif key == 'post_counter':
                file_path = 'Storage/post_counter.txt'
            with open(file_path, 'w') as f:
                f.write(data)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def get(self, key):  # returns dictionary
        try:  # too many put requests, changing it back to local files
            # result = self.s3.Object(self.BUCKET_NAME, key).get()['Body'].read().decode("utf-8")
            if key == 'dict_storage':
                file_path = 'Storage/dict_storage.txt'
            elif key == 'post_counter':
                file_path = 'Storage/post_counter.txt'
            with open(file_path, 'r') as f:
                result = f.read()
            return json.loads(result)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def upload_object(self, file_path, key):  # only for real S3 use
        data = open(file_path, 'rb')
        self.s3.Bucket(self.BUCKET_NAME).put_object(Key=key, Body=data)
