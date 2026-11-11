import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_config(key, default=None):
    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets.get(key, default)
    except Exception:
        return default
