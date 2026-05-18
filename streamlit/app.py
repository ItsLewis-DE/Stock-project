import streamlit as st
import snowflake.connector
import pandas as pd
from pathlib import Path
import os
import logging
_APP_DIR= Path(__file__).resolve().parent
_DEFAULT_LOG_FILE = _APP_DIR / "logs" / "app.log"
log_dir = _APP_DIR / "logs"
log_dir.mkdir(parents=True,exist_ok=True)
VERBOSE = True
LOG_FILE = _DEFAULT_LOG_FILE


#set up log file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemod="a"
)
logger = logging.getLogger("app")

class Background_colors:
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    END = "\033[0m"

def verbose_output(message: str) -> None:
    if VERBOSE:
        print(f"{message}{Background_colors.END}")
conn = snowflake.connector.connect(
    user="SNOWFLAKE_USER",
    password="SNOWFLAKE_PASSWORD",
    account="SNOWFLAKE_ACCOUNT",
    warehouse="SNOWFLAKE_WAREHOUSE",
    DATABASE="SNOWFLAKE_DATABASE",
    SCHEMA="SNOWFLAKE_SCHEMA"
)

menu = st.sidebar.selectbox()