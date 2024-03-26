import streamlit as st
import base64

class Reference:

    ### 
    # Add the pdf file in data directory. Compress the file to be under 1.5 MB
    # Change the PDF_FILE_PATH parameter in data/config.json
    ###

    def get_pdf_display(self,pdf_file_path):
        try:
            with open(pdf_file_path, "rb") as f:
                pdf_bytes = f.read()
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width=100% height="700" type="application/pdf"></iframe>'
        except FileNotFoundError:
            pdf_display = "PDF file not found"
        except Exception as e:
            pdf_display = f"An error occurred: {str(e)}"
        
        return pdf_display

    def main(self):
        st.header("Reference PDF", divider="blue")
        st.write(f"You can refer the original PDF Document [here]({st.session_state.config_param['DOCUMENT_LINK']}).")
