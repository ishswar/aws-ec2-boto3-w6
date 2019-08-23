import json
import sys
from pathlib import Path

import boto3
from botocore.exceptions import NoRegionError, NoCredentialsError
from botocore.exceptions import ClientError


def get_aws_connection():
    try:
        session = getsession()
        s3 = session.resource('s3')
        for bucket in s3.buckets.all():
            break;

        print("Connection to AWS was successful");
        print('Python version: ' + sys.version)
        print('Boto3 version: ' + boto3.__version__)

        return session

    except (NoRegionError, NoCredentialsError) as e:
        print("Error connecting to AWS: " + str(e))
        msg = "The AWS CLI is not configured."
        msg += " Please configure it using instructions at"
        msg += " http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html"
        print(msg);
        sys.exit()


def getsession():
    session = boto3.session.Session()

    return session

