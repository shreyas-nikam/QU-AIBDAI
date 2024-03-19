import re
import streamlit as st
from supabase import create_client, Client

class SignIn:
    def __init__(self):
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        self.table_name: str = st.session_state.config_param["SUPABASE_TABLE_NAME"]
        if 'supabaseDB' not in st.session_state:
            supabase: Client = create_client(url, key)
            st.session_state.supabaseDB = supabase
    
    def validate_email(self,email):
        # Regular expression for basic email validation
        pattern = r'^[a-zA-Z0-9_.+-]+@qusandbox\.com$'
        if re.match(pattern, email):
            return True
        else:
            return False

    # Function to validate full name
    def validate_name(self, name):
        # Regular expression for name validation (alphabetic characters only)
        pattern = r'^[a-zA-Z ]+$'
        if re.match(pattern, name):
            return True
        else:
            return False

    def main(self):
        st.markdown(f"<h1 style='text-align: center;'>{st.session_state.config_param['APP_NAME']}</h1>", unsafe_allow_html=True)
        left_co, cent_co,right_co = st.columns([2,3,2])
        with cent_co:
            index = None
            st.markdown("<p style='text-align: center;'>Enter the following information to proceed.</p>", unsafe_allow_html=True)
        # left_co, cent_co,right_co = st.columns(3)
        # with cent_co:
            name = st.text_input("Name :", placeholder="Enter full name")
            email = st.text_input("Email ID :", placeholder="Enter QuantUniversity email ID")
            agree = st.checkbox(f"""I read and agree to QuantUniversity's [Privacy Policy](https://www.quantuniversity.com/privacy.html)""")            
            
            st.write(' ')
            left_co1, cent_co1,right_co1 = cent_co.columns([.25,.5,.25])
            if cent_co1.button('Proceed', use_container_width = True, type = "primary"):
                if not name:
                    st.error("Please enter your name.")
                elif not self.validate_name(name):
                    st.error("Please enter a valid name (alphabetic characters only).")
                elif not email:
                    st.error("Please enter your email.")
                elif not self.validate_email(email):
                    st.error("Please enter a valid QuantUniversity email address.")
                elif not agree:
                    st.error("Please read and agree the QuantUniversity's [Privacy Policy](https://www.quantuniversity.com/privacy.html).")
                else:
                    data, count = st.session_state.supabaseDB.table(self.table_name).insert({"name":name, "email":email}).execute()
                    print(f"data {data[1][0]}")
                    st.session_state.user_info = data[1][0]
                    print(f"st.session_state.user_info : {st.session_state.user_info['name']}")
                    st.rerun()

            cent_co1.markdown("<p style='text-align: center;'>Not a member? <a href='{url}'>SignUp</a></p>".format(url="https://academy.qusandbox.com/register"), unsafe_allow_html=True)
