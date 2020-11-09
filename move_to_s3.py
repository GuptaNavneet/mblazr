from boto3 import resource
import os
from edgarapp.static.routine.config import AccesseyID,Secret,bucket_name
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


s3 = resource('s3',aws_access_key_id=AccesseyID,aws_secret_access_key=Secret)

#directory = '/mnt/filings-static/capitalrap/edgarapp/static/filings/'
directory = os.path.join(BASE_DIR, 'capitalrap/edgarapp/static/filings/')


try:

    for subdir, dirs, files in os.walk(directory):

        for file in files:
            print(file)
            filepath = subdir + os.sep + file  # actual file
            file_folder = filepath.split('\\')[-2]
            file_to_save = filepath.split('\\')[-1]

            s3.meta.client.upload_file(filepath, bucket_name, 'filings/files/' + file_folder + '/' + file_to_save,
                                       ExtraArgs={'ACL': 'public-read'})
            print('File moved successfully ...Moving to next File')

    print("All items have been moved")
except Exception as e:
    print(e)