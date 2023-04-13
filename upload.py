import os
from datetime import datetime
import concurrent.futures
import time
import argparse
import dropbox
from dropbox.exceptions import AuthError
import pathlib

TOKEN = 'sl.BYNXtX5cDhEKxIOxIhp_K3bZ7IpGu9j5qT1gK8ilR7PWf8LtyUgsq_h-WX-IaxoJozE3ZNQJifQcvHY6qrcaY2ytYHyPdSFHU63VsSx1HmYrBhVlDBUJHx8vvzNK_ZmSKx92Fk3ohp5O'

"""pass argument"""
def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers model on a summarization task")
    # ------------------------>
    parser.add_argument(
        "--token",
        type=str,
        default='sl.BYGei14KeqUNIN85cNV9CMsVjjI_GkXHXldhz0Lwr0X\
            Oe_8HEflnpZFi8XHkF_9N80-kbJzTXoTf22C6uhk_uvyjS1CQRvo\
                WeLw6jki5JOk47JfOK3qUvm0yq6Pvc_ti15T9LB4'
    )
    args, unknown = parser.parse_known_args()
    return args

"""uploadfile to drop box"""
def dropbox_upload_file(local_path, local_file, dropbox_file_path):
    """Upload a file from the local machine to a path in the Dropbox app directory.

    Args:
        local_path (str): The path to the local file.
        local_file (str): The name of the local file.
        dropbox_file_path (str): The path to the file in the Dropbox app directory.

    Example:
        dropbox_upload_file('.', 'test.csv', '/stuff/test.csv')

    Returns:
        meta: The Dropbox file metadata.
    """

    try:
        dbx = dropbox_connect()

        local_file_path = pathlib.Path(local_path) / local_file

        with local_file_path.open("rb") as f:
            meta = dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode("overwrite"))
            print(f'{local_file} upload success (ノ´∀｀)ノ')
            return meta

        
    except Exception as e:
        print('Error uploading file to Dropbox: ' + str(e))

def dropbox_connect(access_token=TOKEN):
    """Create a connection to Dropbox."""

    try:
        dbx = dropbox.Dropbox(access_token)
    except AuthError as e:
        print('Error connecting to Dropbox with access token: ' + str(e))
    return dbx

'''main'''
if __name__ == '__main__':
    args = parse_args()
    # get current date
    TODAY = str(datetime.now().strftime("%Y-%m-%d"))
    print(TODAY)

    # assign upload filename
    local_paths = [
        f'./shopLst/{TODAY}/',
        f'./meau_Foodpanda/'
        ]
    local_files = [
        f'all_most_{TODAY}.csv',
        f'foodpandaMenu_{TODAY}.csv'
    ]

    dropbox_connect() # connect to dropbox
    # uploadshopLst
    for (path, file) in zip(local_paths, local_files):
        dropbox_file_path = f'/{TODAY}/{file}'
        dropbox_upload_file(
            local_path=path,
            local_file=file,
            dropbox_file_path=dropbox_file_path,
        )
