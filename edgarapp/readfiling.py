from boto3 import client, resource

AccesseyID='AKIASSCKYNFNNKTWSDOE'
Secret="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"

client = client('s3')
s3 = resource('s3', aws_access_key_id=AccesseyID, aws_secret_access_key=Secret)
bucket_name='mblazr'

def readFiling(file):
    try:
        response = s3.Object(bucket_name, 'filings/files/'+file).get()['Body'].read()
    except:
        response = ''

    return response


