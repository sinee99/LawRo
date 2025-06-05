# s3.py

import boto3
import os
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

def connection_s3():
    """
    connection aws s3 user

    Returns:
        s3_client: aws s3 user
    """
    try:
        print("connection_s3 start")

        s3_client = boto3.client(service_name="s3",
                                 aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        return s3_client
    except Exception as e:
        print(e)
        raise
    finally:
        print("connection_s3 end")

if __name__ == "__main__":
    try:
        s3_client = connection_s3()
        print(s3_client)
    except Exception as e:
        print(e)
    finally:
        print("bucket finish")
