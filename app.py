## Q & A Chatbot using Ollama

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# # from langchain_community.llms.ollama import Ollama
# from langchain_ollama import OllamaLLM
# import streamlit as st
# import os

# from dotenv import load_dotenv
# load_dotenv()

# ## Langsmith tracking
# os.environ['LANGCHAIN_API_KEY']=os.getenv('LANGCHAIN_API_KEY')
# os.environ['LANGCHAIN_TRACING_V2']="true"
# os.environ["LANGCHAIN_PROJECT"]="Q&A Chatbot With OLLAMA"

# ## Prompt template
# prompt=ChatPromptTemplate.from_messages(
#     [
#         ("system","You are a helpful assistant. Please response to the user queries."),
#         ("user","Question:{question}")
#     ]
# )

# def generate_response(question,llm):
#     llm=OllamaLLM(model=llm)
#     output_parser=StrOutputParser()
#     chain=prompt|llm|output_parser
#     answer=chain.invoke({'question':question})
#     return answer

# ## Drop down to select various Open AI models
# llm=st.sidebar.selectbox("Select an Open AI Model",["gemma2:2b"])

# ## Adjust response parameter
# temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)
# max_tokens=st.sidebar.slider("Max Tokens",min_value=50,max_value=300,value=150)

# ## Main interface for user input
# st.write("Go ahead and ask any question")
# user_input=st.text_input("You:")

# if user_input:
#     response=generate_response(user_input,llm)
#     st.write(response)
# else:
#     st.write("Please provide the query")
    


## RAG Document Q&A using GROQ API and llama3

# import os
# import streamlit as st
# from langchain_groq import ChatGroq
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import create_retrieval_chain
# from langchain_community.vectorstores import FAISS
# from langchain_community.document_loaders import PyPDFDirectoryLoader

# from dotenv import load_dotenv
# load_dotenv()

# ## Load the GROQ API Key
# os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
# groq_api_key=os.getenv("GROQ_API_KEY")

# llm=ChatGroq(groq_api_key=groq_api_key,model_name="gemma2-9b-it")

# prompt=ChatPromptTemplate.from_template(
#     """
#      Answer the questions based on the provided context only.
#      Please provide the most accurate response based on the question
#      <context>
#      {context}
#      <context>
#      Question:{input}
#     """
# )

# def create_vector_embeddings():
#     if "vectors" not in st.session_state:
#         st.session_state.embeddings=OllamaEmbeddings()
#         st.session_state.loader=PyPDFDirectoryLoader("research_papers") ## Data Ingestion step
#         st.session_state.docs=st.session_state.loader.load() ## Document loading
#         st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
#         st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
#         st.session_state.vectors=FAISS.from_documents(st.session_state.final_documents,st.session_state.embeddings)

# user_prompt=st.text_input("Enter your query from the research paper")

# if st.button("Document Embedding"):
#     create_vector_embeddings()
#     st.write("Vector database is ready")
    
# import time

# if user_prompt:
#     document_chain=create_stuff_documents_chain(llm,prompt)
#     retriever=st.session_state.vectors.as_retriever()
#     retrieval_chain=create_retrieval_chain(retriever,document_chain)
    
#     start=time.process_time()
#     response=retrieval_chain.invoke({'input':user_prompt})
#     print(f"Response time :{time.process_time()-start}")
    
#     st.write(response['answer'])
    
#     ## With a streamlit expander
#     with st.expander("Document similarity search"):
#         for i,doc in enumerate(response['context']):
#             st.write(doc.page_content)
#             st.write('-------------------------')

## RAG Q&A Conversation with PDF including chat history

import streamlit as st 
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os 

from dotenv import load_dotenv
load_dotenv()

os.environ['HUGGINGFACE_ACCESS_TOKEN']=os.getenv('HUGGINGFACE_ACCESS_TOKEN')
embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

## Setup Streamlit
st.title("Conversational RAG with PDF uploads and Chat history")
st.write("Upload Pdf's and chat with their content")

## Input the Groq Api key
api_key=st.text_input("Enter you GROQ API KEY:",type="password")

## Check if groq api key is provided
if api_key:
    llm=ChatGroq(groq_api_key=api_key,model_name="gemma2-9b-it")
    
    ## Chat interface
    session_id=st.text_input("Session ID",value="default_session")
    
    ## statefully manage chat history
    if 'store' not in st.session_state:
        st.session_state.store={}
    
    uploaded_files=st.file_uploader("Choose A PDF file",type="pdf",accept_multiple_files=True)
    ## Process uploaded PDF's
    
    if uploaded_files:
        documents=[]
        for uploaded_file in uploaded_files:
            temppdf=f"./temp.pdf"
            with open(temppdf,"wb") as file:
                file.write(uploaded_file.getvalue())
                file_name=uploaded_file.name
                
            loader=PyPDFLoader(temppdf)
            docs=loader.load()
            documents.extend(docs)
            
        ## Split and create embeddings for the documents
        # text_splitter=RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
        # splits=text_splitter.split_documents(documents)
        # vectorstore = Chroma.from_documents(documents=splits,embedding=embeddings)
        # retriever=vectorstore.as_retriever()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory="./chroma_db",
            collection_name="pdf_collection"
        )
        retriever = vectorstore.as_retriever()
        
        contextualize_q_system_prompt=(
            "Given a chat history and the latest user question"
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system",contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human","{input}")
        ])
        
        history_aware_retriever=create_history_aware_retriever(llm,retriever,contextualize_q_prompt)
        
        ## Question Answer prompt
        system_prompt=(
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}" 
        )
        
        qa_prompt=ChatPromptTemplate.from_messages(
            [
                ("system",system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human","{input}")
            ]
        )
        
        question_answer_chain=create_stuff_documents_chain(llm,qa_prompt)
        rag_chain=create_retrieval_chain(history_aware_retriever,question_answer_chain)
        
        def get_session_history(session:str)->BaseChatMessageHistory:
            if session_id not in st.session_state.store:
                st.session_state.store[session_id]=ChatMessageHistory()
            return st.session_state.store[session_id]
        
        conversational_rag_chain=RunnableWithMessageHistory(
            rag_chain,get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"        
        )
        
        user_input = st.text_input("Your question:")
        if user_input:
            session_history=get_session_history(session_id)
            response=conversational_rag_chain.invoke(
                {"input":user_input},
                config={
                    "configurable":{"session_id":session_id}
                },
            )
            # st.write(st.session_state.store)
            # st.write("Assistant:",response['answer'])
            st.write(response['answer'])
            # st.write("Chat history:",session_history.messages)
else:
    st.warning("Please enter the GROQ API KEY")
        
    
    