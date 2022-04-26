
from os import environ
from dotenv import load_dotenv  

"""
looks for a file named .env in the current directory and
 will add all the variable definitions in it to the os.environ dictionary.
If a .env file is not found in the current directory, 
then the parent directory is searched for it. 
The search keeps going up the directory hierarchy 
until a .env file is found or the top-level directory is reached.
"""
#load_dotenv('./.env') 
# the path can be explicitly passed as an argument,
# to prevent python-dotenv from searching for a .env file through your directories
load_dotenv()

region=environ.get('REGION')# returns the string value or None otherwise
access_key_id=environ.get('ACCESS_KEY')
secret_access_key=environ.get('SECRET_KEY')
time_interval=environ.get('TIME_INTERVAL')
session_token=environ.get('SESSION_TOKEN')
endpoint=environ.get('ENDPOINT')