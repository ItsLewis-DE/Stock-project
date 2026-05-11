import json
import pendulum
import requests
import pathlib,logging
from dotenv import load_dotenv

def read_newest_file(dirpath,extension):
    logger = logging.getLogger(__name__)
    path = Path(dirpath)
    if not path.exist():
        logger.error("Can not found file!!")
        raise
    files = [file for file in path.iterdir() 
             if file.isfile() and file.suffix == extension
            ]
    if not files:
        return None
    newest_file = max(
        files,
        key = lambda file : file.stat().st_mtime
    )
    return newest_file
