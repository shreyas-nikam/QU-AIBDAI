# Import libraries
import os
import sys
import re
import streamlit as st
import json
import pandas as pd

class Home:
    ### 
    # This is home page of the application.

    # Change the Application name and Document link in data/config.json by
    # updating parameters "APP_NAME" and "DOCUMENT_LINK"
    
    ###

    def main(self):
        document_link = st.session_state.config_param["DOCUMENT_LINK"]
        st.header(st.session_state.config_param["APP_NAME"], divider= "blue")
        st.markdown("""
        ### Introduction

        - The spectrum of effective attacks against ML is wide, rapidly evolving, and covers all phases of the ML life cycle - from design and implementation to training, testing, and finally, to deployment in the real world.
        - This demo is intended to be a step toward developing a taxonomy and terminology of adversarial machine learning (AML), which in turn may aid in securing applications of artificial intelligence (AI) against adversarial manipulations of AI systems.
        - We adopt the notions of security, resilience, and robustness of ML systems from the NIST AI Risk Management Framework
                    
        ### Usage Guide

        - Course Materials: Slides and Video of the 12 modules
        - Demo: Coming soon...
        - QuBot: Ask me anything regarding the NIST Adversarial Module
        - Quiz and Certificate: Test your understanding and obtain a certificate of completion
        - Reference PDF: Original publication
 
        """, unsafe_allow_html=True)
        st.divider()
        st.caption("© 2021 [QuantUniversity](https://www.quantuniversity.com/). All Rights Reserved.")
        st.caption(f"The purpose of this demonstration is solely for educational use and illustration. To access the full legal documentation, please visit [this link]({document_link}). Any reproduction of this demonstration requires prior written consent from QuantUniversity.")
