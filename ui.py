# Funções relacionadas à interface Streamlit
from logic import process_comparison
import streamlit as st

def app():
    st.set_page_config(page_title="PagerDuty x ServiceNow Customizations Comparator", layout="wide")
    st.title("🧠 PagerDuty x ServiceNow Customizations Comparator with LangChain + Ollama")

    
from logic import process_comparison
import streamlit as st
from lxml import etree
import os

def app():
    st.set_page_config(page_title="PagerDuty x ServiceNow Customizations Comparator", layout="wide")
    st.title("🧠 PagerDuty x ServiceNow Customizations Comparator with LangChain + Ollama")

    BASE_VERSION_PATHS = {
        "v7.6": "base_versions/v7.6.xml",
        "v7.9.1": "base_versions/v7.9.1.xml",
        "v8.0.1": "base_versions/v8.0.1.xml",
        "v8.1.0": "base_versions/v8.1.0.xml"
    }

    selected_version = st.selectbox("📦 Select base version to compare against:", list(BASE_VERSION_PATHS.keys()))
    base_cache_path = BASE_VERSION_PATHS[selected_version]
    uploaded_custom = st.file_uploader("📂 Upload the customized file", type=["xml"], key="custom")

    if os.path.exists(base_cache_path) and uploaded_custom:
        base_tree = etree.parse(base_cache_path)
        custom_tree = etree.parse(uploaded_custom)
        process_comparison(base_tree, custom_tree)
