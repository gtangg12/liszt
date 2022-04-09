import os
import atexit

from datetime import datetime
from time import sleep
from re import L

import io
import tweepy
import config

import paramiko
from dotenv import load_dotenv


def OAuth():
    try:
        auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret_key)
        auth.set_access_token(config.access_token, config.access_token_secret)
        return auth
    except Exception as e:
        return None

def upload():
    oauth = OAuth()
    api = tweepy.API(oauth)
    upload_result = api.media_upload('video.mp4')
    api.update_status(status="video tweet", media_ids=[upload_result.media_id_string])


def generate_video():
    load_dotenv()
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    key_string = os.environ['WZHAO6_PRIVATE_KEY'].replace('\\n', '\n')
    key = paramiko.RSAKey.from_private_key(io.StringIO(key_string))
    client.connect('satori-login-002.mit.edu',
                username='wzhao6',
                pkey=key)

    sftp = client.open_sftp()
    today = datetime.now().strftime('%Y-%m-%d')

    print('Generating video...')

    stdin, stdout, stderr = client.exec_command('bash /nobackup/users/wzhao6/minerva-action/satori/run.sh')

    while True:
        sleep(300) #need update this parameter
        print('Checking for video...')
        if today in sftp.listdir('/nobackup/users/wzhao6/minerva-action/satori/data/'):
            break
        print('Video not ready yet...')
        print('Got error: ', stderr.read())
        print('Got output: ', stdout.read())

        # with sftp.open('/nobackup/users/wzhao6/minerva-action/satori/minerva-action.out', 'r') as f:
        #     print('Got Satori output: ', f.read())
        # with sftp.open('/nobackup/users/wzhao6/minerva-action/satori/minerva-action.out', 'w') as f:
        #     f.write('')
        # with sftp.open('/nobackup/users/wzhao6/minerva-action/satori/minerva-action.err', 'r') as f:
        #     print('Got Satori error: ', f.read())
        # with sftp.open('/nobackup/users/wzhao6/minerva-action/satori/minerva-action.err', 'w') as f:
        #     f.write('')

    sftp.get('/nobackup/users/wzhao6/minerva-action/satori/data/' + today + '/combined.mp4', 'video.mp4')

    sftp.close()
    client.close()

def main():
    #generate_video()
    #upload()
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'Logged at {today}')

if __name__ == "__main__":
    main()
