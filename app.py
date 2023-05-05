import os
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from flask import Flask, render_template, request
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["TIMEOUT"] = 120


file_input = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyse")
def analyse():
    return render_template("analyse.html")
    
@app.route("/email")
def email():
    return render_template("email.html")

@app.route("/translate")
def translate():
    return render_template("Translate.html")

@app.route("/upload", methods=["POST"])
def upload():
    global file_input
    files = request.files.getlist("files[]")
     
    # fileType = request.form["type"]
    myquestion = request.form["myquestion"]

    # # Do something with the uploaded file
    result = qa_result(files, myquestion)
    return json.dumps(result)


def read_pdf(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def read_docx(docx):
    doc = Document(docx)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)


def read_txt(txt):
    return txt.read().decode("utf-8")


def read_csv(csv):
    df = pd.read_csv(csv)
    return df.to_string()


def read_excel(xls):
    df = pd.read_excel(xls)
    return df.to_string()


def qa_result(docs, user_question):
    # Upload multiple files
    # docs = st.file_uploader("Upload your documents", type=["pdf", "doc", "docx", "txt", "csv", "xls", "xlsx"], accept_multiple_files=True)

    combined_text = ""
 

    for doc in docs:
        if doc.content_type == "application/pdf":
            text = read_pdf(doc)
        elif doc.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(doc)
        elif doc.content_type == "text/plain":
            text = read_txt(doc)
        elif doc.content_type == "text/csv":
            text = read_csv(doc)
        elif doc.content_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            text = read_excel(doc)
        else:
            return "Unsupported file format. Please upload a supported file."
            
        combined_text += "\n" + text

    # split into chunks
    
        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
        )
        chunks = text_splitter.split_text(combined_text)

        if not chunks:
            return "No valid text data found in the uploaded documents. Please check the contents and try again."

        # create embeddings
        embeddings = OpenAIEmbeddings(openai_api_key='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')
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        # show user input
        # user_question = st.text_input("Ask a question about your documents:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)

            llm = OpenAI(openai_api_key='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')
            chain = load_qa_chain(llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=user_question)
                print(cb)

            return response
    return " Please upload documents."

if __name__ == "__main__":
    app.run()
