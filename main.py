import json
import streamlit as st
import pandas as pd 
from src.signIn import SignIn
from src.home import Home
from src.chatBot import ChatBot
from src.courseMaterial import CourseMaterial
from src.reference import Reference
from src.quiz import Quiz



if "user_info" not in st.session_state:
    st.session_state.user_info = {}

if "config_param" not in st.session_state:
    with open("./data/config.json", 'r') as file:
        json_data = file.read()
    st.session_state.config_param = json.loads(json_data)

if "page_chatbot" not in st.session_state:
    st.session_state.page_chatbot = ChatBot()
    st.session_state.page_home = Home() 
    st.session_state.page_signIn = SignIn() 
    st.session_state.page_quiz = Quiz()
    st.session_state.page_reference = Reference()
    st.session_state.page_courseMaterial = CourseMaterial()


st.set_page_config(page_title=st.session_state.config_param["APP_NAME"],layout="wide", page_icon="🏬")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg", use_column_width="always")
# Set sidebar routes
page = st.sidebar.radio("Select a Page:", ["Home", "Course Material","QuBot", "Quiz", "Reference PDF"], 
    disabled= True if not st.session_state.user_info else False)

# check if the content is updated

if not st.session_state.user_info:
    st.session_state.page_signIn.main()    
else:
    if page == "Home":
        st.session_state.page_home.main()
    elif page == "Course Material":
        st.session_state.page_courseMaterial.main()
    elif page == "QuBot":
        st.session_state.page_chatbot.main()
    elif page == "Quiz":
        st.session_state.page_quiz.main()
    elif page == "Reference PDF":
        st.session_state.page_reference.main()
