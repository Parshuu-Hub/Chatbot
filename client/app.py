import streamlit as st
from components.chatUI import render_chat
from components.history_download import render_history_download
from components.upload import render_uploader

st.set_page_config(page_title="AI Assistant",layout="wide")
st.title("Chatbot Assistant")

render_uploader()
render_chat()
render_history_download()
