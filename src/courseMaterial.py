import streamlit as st
import streamlit.components.v1 as components
import fitz  # PyMuPDF
import io
from PIL import Image
from src.s3.getFiles import fetch_updated_files

###
# add videos in data/videos directory and update video locations by changing the parameter "VIDEOS_LINKS" in data/config_param.json 
# update course_links locations by changing the parameter "COURSE_LINKS" in data/config_param.json 
# add transcripts in data/transcripts directory and update transcripts locations by changing the parameter "TRANSCRIPTS_FILES" in data/config_param.json 
###

class CourseMaterial:
    

    def __init__(self):
        if "course_index" not in st.session_state:
            st.session_state.course_index = 0
            st.session_state.page_num = 0
    
        
        print(st.session_state.course_index)
        self.course_links = st.session_state.config_param["COURSE_LINKS"]
        self.course_names = st.session_state.config_param["COURSE_NAMES"]
        self.videos = st.session_state.config_param["VIDEOS_LINKS"]
        self.transcripts = st.session_state.config_param["TRANSCRIPTS_FILES"]
        

    def main(self):

        st.header("Course Materials", divider="blue")
        if "last_updated" not in st.session_state:
            with st.spinner("Fetching latest content..."):
                fetch_updated_files()
                st.session_state.last_updated = True

        t1, t2 = st.tabs(["Video", "Slides"])

        def slide_handle_change():
            st.session_state.course_index = st.session_state.config_param["COURSE_NAMES"].index(st.session_state.slides_nav)
            st.session_state.page_num = 0
        def video_handle_change():
            st.session_state.course_index = st.session_state.config_param["COURSE_NAMES"].index(st.session_state.video_nav)

        with t1:
            nav, content = st.columns([2,8])
        
            with nav.container(border=True):
                course1 = nav.radio("Modules",self.course_names, index=st.session_state.course_index, key = "video_nav", on_change=video_handle_change)
            # st.session_state.course_index = st.session_state.config_param["COURSE_NAMES"].index(course1)
            content.video(self.videos[st.session_state.course_index])
            
            _, col = st.columns([8, 2])
            f = open(self.transcripts[st.session_state.course_index], encoding='utf-8', errors='ignore').read()

            col.download_button("Download Transcript", f, file_name="transcript.txt")
            
        with t2:
            nav, content = st.columns([2,8])
            with nav.container(border=True):
                course2 = nav.radio("Modules",self.course_names, index=st.session_state.course_index, key = "slides_nav", on_change=slide_handle_change)    
            
            with content: 
                with st.spinner('Wait for it...'):
                    url = self.course_links[st.session_state.course_index]

                    # ile_path = "path/to/local.pptx"

                    # Generate HTML code to embed the PowerPoint presentation
                    # html_code = f'<iframe src="https://view.officeapps.live.com/op/embed.aspx?src={file_path}" width="100%" height="600px" frameborder="0"> </iframe>'
                    # st.markdown(html_code, unsafe_allow_html=True)
                    # st.markdown(f'<iframe src="{url}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
                    # Display current page as image
                    doc = fitz.open(url)

                    # if 'page_num' not in st.session_state:
                    #     st.session_state.page_num = 0  # starting from the first page

                    total_pages = len(doc)

                    def display_page(page_num):
                        page = doc.load_page(page_num)  # load the page
                        pix = page.get_pixmap()  # render page to an image
                        img = Image.open(io.BytesIO(pix.tobytes()))
                        st.image(img, use_column_width=True)

                    display_page(st.session_state.page_num)
                                        
                    # Navigation buttons
                    col1, _, center, _, col2 = st.columns([1, 4, 1, 4, 1])
                    with col1:
                        if st.button('⇦'):
                            if st.session_state.page_num > 0:
                                st.session_state.page_num -= 1
                                st.rerun()

                    with col2:
                        if st.button('⇨'):
                            if st.session_state.page_num < total_pages - 1:
                                st.session_state.page_num += 1
                                st.rerun()

                    with center:
                        st.caption(f'Page {st.session_state.page_num + 1}/{total_pages}')

            
            col1, col2, col3 = st.columns([0.1,0.6,0.1])
            with col1:
                if st.session_state.course_index>0:
                    
                    if st.button("Previous Module"):
                        st.session_state.course_index-=1
                        st.session_state.page_num = 0
                        st.rerun()            
        
            with col3:
                if st.session_state.course_index<len(self.course_links):
                    
                    if st.button("Next Module"):
                        st.session_state.course_index+=1
                        st.session_state.page_num = 0
                        st.rerun()