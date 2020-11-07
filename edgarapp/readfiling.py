from boto3 import client, resource
#from capitalrap.settings import AccesseyID,Secret,bucket_name
from .static.routine.config import AccesseyID,Secret,bucket_name

client = client('s3')
s3 = resource('s3', aws_access_key_id=AccesseyID, aws_secret_access_key=Secret)


def readFiling(file):
    try:
        response = s3.Object(bucket_name, 'filings/files/'+file).get()['Body'].read()
    except:
        response = ''

    return response


