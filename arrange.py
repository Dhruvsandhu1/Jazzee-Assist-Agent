from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain.retrievers import BM25Retriever,EnsembleRetriever
from dotenv import load_dotenv
# from rerankers import jina_reranker
from datetime import datetime
import sqlite3
import uuid
import pickle
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# JINA_KEY = os.getenv("JINA_KEY")
# reranker = jina_reranker(JINA_KEY)
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_query TEXT,
    gpt_response TEXT,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                 (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages

def docs2str(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_query TEXT,
    gpt_response TEXT,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                 (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages

def retrieve_chroma(product):
    vectorstore = Chroma(persist_directory="./chroma3_db",embedding_function=embedding_function,collection_name=product)
    return vectorstore

def retreive_chunks(product, filename="product_chunks.pkl"):
    with open(filename, "rb") as file:
        product_chunks = pickle.load(file)
    print(f"Product chunks loaded from {filename}!")
    chunks = product_chunks[product]
    return chunks


DB_NAME = "rag_app.db"
llm = ChatOpenAI(model="gpt-4o",api_key=api_key)
template=(
          """Answer the question based only on the following context:
{context}
Question: {question}
Answer: """
)
session_id = str(uuid.uuid4())
create_application_logs()

contextualize_q_system_prompt = """
Given a chat history and the latest user question
which might reference context in the chat history,
formulate a standalone question which can be understood
without the chat history. Do NOT answer the question,
just reformulate it if needed and otherwise return it as is.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
        ("system", "Context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])



prompt = ChatPromptTemplate.from_template(template)

# def rerank_chunks(user_question, chunks, top_k=10):
#     """
#     Rerank retrieved chunks using Jina.
#     """
#     if not chunks:
#         return []

#     chunk_texts = [chunk["content"] for chunk in chunks]  # Use 'content' as the main field
#     # reranked = reranker.rerank_with_jina(user_question, chunk_texts, top_k)
#     reranked_chunks = [(chunks[item["index"]], item["relevance_score"]) for item in reranked["results"]]

#     for chunk, score in reranked_chunks:
#         chunk["reranker_score"] = score

#     return sorted(reranked_chunks, key=lambda x: x[1], reverse=True)



def fetch_reviews(product,query):
    try:
        vectorstore = retrieve_chroma(product)
        chunks = retreive_chunks(product)
        # reranked_chunks = rerank_chunks(query, chunks)
        chroma_retriever = vectorstore.as_retriever()
        bm25_retriever = BM25Retriever.from_documents(documents=chunks)
        retriever = EnsembleRetriever(retrievers=[bm25_retriever,chroma_retriever],weights=[0.25,0.75])
        
        # rag_chain = (
        # {"context": retriever | docs2str, "question": RunnablePassthrough()}
        # | prompt
        # | llm
        # | StrOutputParser()

        # )
        history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
        )
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        chat_history = get_chat_history(session_id)
        answer = rag_chain.invoke({"input": query, "chat_history": chat_history})['answer']
        insert_application_logs(session_id, query, answer, "gpt-4o")
        return answer
    except:
        return "Some error occured.Please try reloading the page or try after after some time."
    