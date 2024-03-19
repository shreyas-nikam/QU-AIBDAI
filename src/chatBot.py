import time
import ast
import streamlit as st
from src.ui.chatUI import display_on_chat
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.prompts import BasePromptTemplate, PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_openai import OpenAIEmbeddings

from src.customHybridRetriever import Retriever

class ChatBot:
    def __init__(self):
        OPENAI_KEY = st.secrets["OPENAI_KEY"]
        self.OPENAI_MODEL =  st.secrets["OPENAI_MODEL"]
        self.TOTAL_QUES = st.session_state.config_param["QUIZ_TOTAL_QUES"]
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_KEY)
        self.chatModel = ChatOpenAI(temperature=0, model_name = self.OPENAI_MODEL,openai_api_key = OPENAI_KEY)
        self.chatHistory = ""
        self.retriever = Retriever()
        # self.retriever.create_vector_store(file_name="./data/content.txt")
    
    def get_context(self, question, path = "./data/text_to_vector_db"):
        return self.retriever.parse_response_with_rerank(question)
    
    def resolve_question(self, question):
        prompt = """
Generate the OUTPUT QUESTION based on the following examples for the last query.

HISTORY:
[]
NOW QUESTION: Hello, how are you?
NEED COREFERENCE RESOLUTION: No => THOUGHT: Consequently, the output question mirrors the current query.
OUPUT QUESTION: Hello, how are you?
-------------------
HISTORY:
[User: Is Milvus a vector database?
You: Yes, Milvus is a vector database.]
NOW QUESTION: How to use it?
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: I must substitute 'it' with 'Milvus' in the current question.
OUTPUT QUESTION: How to use Milvus?
-------------------
HISTORY:
[]
NOW QUESTION: What are its features?
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: Although 'it' requires substitution, there's no suitable reference in the history. Thus, the output question remains unchanged. 
OUTPUT QUESTION: What are its features?
-------------------
HISTORY:
[User: What is PyTorch?
You: PyTorch is an open-source machine learning library for Python. It provides a flexible and efficient framework for building and training deep neural networks.
User: What is Tensorflow?
You: TensorFlow is an open-source machine learning framework. It provides a comprehensive set of tools, libraries, and resources for building and deploying machine learning models.]
NOW QUESTION: What is the difference between them?
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: 'Them' should be replaced with 'PyTorch and Tensorflow' in the current question.
OUTPUT QUESTION: What is the difference between PyTorch and Tensorflow?
-------------------
HISTORY:[
{history}
]
NOW QUESTION: {question}
NEED COREFERENCE RESOLUTION:
OUTPUT QUESTION: 
        """
        llm = ChatOpenAI(model=self.OPENAI_MODEL, temperature=0, api_key=st.secrets["OPENAI_KEY"])
        prompt = PromptTemplate(
            template=prompt,
            input_variables=["history", "question"]
        )

        _input = prompt.format_prompt(history=self.chatHistory, question=question)
        print(_input)
        output = llm(_input.to_messages())
        return output.content

    def get_response(self,question):
        question = self.resolve_question(question)
        print("RESOLVED QUESTION::",question)
        response_schemas = [
                ResponseSchema(name="answer", description="Your answer to the given question",type = 'markdown'),
                ResponseSchema(name="followup_questions", description="A list of 3 follow-up questions that the user may have based on the question.", type = 'list')
            ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()

        context = self.get_context(question)
        print("Context::", context)

        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template("""
Answer the given question using the provided context only. 
You have to return 2 things :
1. A conversational reponse to the question below using the context and previous conversation only. 
2. A list of three related follow-up questions to the question that the user might have. Do not repeat the suggested questions. 

{format_instructions}

DONT FORGET TO PUT COMMA(,) between the keys in JSON output
                                                
History:
{history}

Context:
{context}


Question:
{question}

If the answer is not present in the context, return "Please provide more context to answer the question. Please check the official reference pdf here: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2023.ipd.pdf".
            """)
            ],
            input_variables=["history","context","question"],
            partial_variables={"format_instructions": format_instructions}
        )
        _input = prompt.format_prompt(history = self.chatHistory, context = context, question=question)
        output = self.chatModel(_input.to_messages())
        
        validJSON = False
        runs = 0
        while (validJSON == False):
            try:
                json_output = output_parser.parse(output.content)
                validJSON = True
                self.chatHistory += f"""\n
                User: {question}
                You: {str(json_output['answer'])}"""
                print("History::",self.chatHistory)
            except Exception as e :
                print(f"Error : {e}")
                runs+=1
                if runs < 4:
                    print(f"\n\n Retry No ::{runs}")
                    error_prompt = ChatPromptTemplate(
                        messages=[
                                HumanMessagePromptTemplate.from_template(""" 
                                Error encountered: {e}

                                Regenerate the previous answer with proper JSON format
                                DO NOT FORGET TO PUT COMMA(,) between the keys in JSON output
                                {format_instructions}

                                {history}

                                Extracted Da
                                You:
                                {context}

                                Question:
                                {question}""")
                                ],
                        input_variables=["e","history","context","question"],
                        partial_variables={"format_instructions": format_instructions}
                    )
                    _error_input = error_prompt.format_prompt(e=e,history = self.chatHistory,context = context, question=question)
                    print(f"_error_input:: \n{_error_input}")
                    output = self.chatModel(_error_input.to_messages())
                else:
                    return {'answer': f"Something went wrong! Please try again!",
                        'followup_questions': []}
                    

        return json_output

    
            
    def main(self):
        # @st.cache_resource
        
        if "keyOwner" not in st.session_state:
            st.session_state.keyOwner = "QU"


        name = st.session_state.user_info['name']
        if "response" not in st.session_state:
            st.session_state.ques_session = True
            st.session_state.response = {'answer': f'Hello {name}! How can I help you today? ',
                            'followup_questions': ["What are some of the applications of NLU in Investments?",
                                                    "Tell me more about Knowledge Graphs.",
                                                    "What is Intelligent Customer Service in Insurance?",
                                                    ]}
        #front-end chatmemory
        INITIAL_MESSAGE = [{"role": "assistant",
                "content": f'Hello {name}! How can I help you today? '}]
        if "messages" not in st.session_state:
            st.session_state["messages"] = INITIAL_MESSAGE

        if "question_per_session" not in st.session_state:
            st.session_state.question_per_session = 0

        def send_prompt(prompt):
            # if "limit_reached" not in st.session_state and st.session_state.question_per_session < self.TOTAL_QUES:
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_on_chat(prompt, is_user =True) #user
                
                with st.spinner('Getting you the answer'):
                    time.sleep(1)
                    st.session_state.response = self.get_response(prompt)

                answer = st.session_state.response["answer"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.ques_session = True
                st.session_state.question_per_session += 1
                if st.session_state.question_per_session == self.TOTAL_QUES:
                    st.session_state.keyOwner = 'None'
                st.rerun()
            

        # st.markdown("<h1 style='text-align: Left;'>NIST QuBot</h1>", unsafe_allow_html=True)
        
        st.header("QuBot", divider= "blue")
        st.markdown("""
        <p style='text-align: left; font-size:12px;'><i>Note:</i><br>
            <i>Qubot</i> is an experimental AI-bot that utilizes information from a published <a href="{url}">document</a>. You can experiment with Qubot a few times for free. Later, you can use your own <a href="{key_link}">OpenAI key</a> for further usage.
        </p>
        """.format(url="https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page", key_link="https://platform.openai.com/docs/quickstart#:~:text=First%2C%20create%20an%20OpenAI%20account,not%20share%20it%20with%20anyone"), unsafe_allow_html=True)

        if st.session_state.keyOwner != "None" :
            for message in st.session_state.messages:
                display_on_chat(
                    message["content"],
                    True if message["role"] == "user" else False,
                )
            if type(st.session_state.response["followup_questions"]) == str:
                followup_questions = ast.literal_eval(st.session_state.response["followup_questions"])
            else:
                followup_questions = st.session_state.response["followup_questions"]

            col0, col1, col2, col3, col5 = st.columns([0.05,0.30,0.30,0.30,0.05])

            btn1,btn2,btn3 = False,False,False

            if st.session_state.response["followup_questions"] != [] and len(st.session_state.response["followup_questions"]) == 3:
                with col1:
                    ques1 = followup_questions[0]
                    btn1 = st.button(ques1)
                
                with col2:
                    ques2 = followup_questions[1]
                    btn2 = st.button(ques2)

                with col3:
                    ques3 = followup_questions[2]
                    btn3 = st.button(ques3)

            if prompt := st.chat_input():
                    send_prompt(prompt) 

            if btn1:
                send_prompt(ques1)
            if btn2:
                send_prompt(ques2)
            if btn3:
                send_prompt(ques3)

        else:
            st.warning("You have exhausted your free trial. Enter your OpenAI key below to conitnue")
            # input_content, btn_content = st.columns([0.8,0.2])
            OPENAI_KEY = st.text_input('OpenAI key:',type="password")

            if st.button("Submit Key", type="secondary"):
                self.chatModel = ChatOpenAI(temperature=0, model_name = self.OPENAI_MODEL,openai_api_key = OPENAI_KEY)
                st.session_state.keyOwner = "USER"
                st.rerun()



