import os
from dotenv import load_dotenv # type: ignore
import streamlit as st # type: ignore
load_dotenv()

def get_variable(name):
    if hasattr(st, 'secrets') and name in st.secrets:
        return st.secrets[name]
    return os.getenv(name)

GEMINI_API_KEY = get_variable('AIzaSyDjFxG6R22fNPDq41hvfpXOWAbOI_9V3CQ')
GROQ_API_KEY = get_variable('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')
REPLICATE_API_TOKEN = get_variable('r8_ZKE5Q1FmECadmHnfiPdNybA5mCsRgU43Kj6sO')
HG_API_KEY = get_variable('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')