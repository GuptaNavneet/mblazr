from boto3 import resource,client
from capitalrap.settings import AccesseyID,Secret,bucket_name
import os


s3 = resource('s3',aws_access_key_id=AccesseyID,aws_secret_access_key=Secret)

directory = '/mnt/filings-static/capitalrap/edgarapp/static/filings/'
try:
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            filepath = subdir + os.sep + filename  # actual file
            file_folder = filepath.split('\\')[-2]
            file_to_save = filepath.split('\\')[-1]

            s3.meta.client.upload_file(filepath, bucket_name, 'filings/files/' + file_folder + '/' + file_to_save,
                                       ExtraArgs={'ACL': 'public-read'})
            print('File moved successfully ...Moving to next File')

    print("All items have been moved")
except Exception as e:
    print(e)
