# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Tutorial For Langchain

import os
os.environ["OPENAI_API_KEY"] = "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"

# ### Define the GPT Model to use.

# +
from langchain_openai import ChatOpenAI
from typing import List
import glob

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

# +
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_markdown_files(file_paths) -> List[Document]:
    """
    Parse all the markdown files into Documents.

    :param file_paths: list of md file_paths
    """
    documents = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Create a Document object for each file
        documents.append(Document(page_content=content, metadata={"source": file_path}))
    return documents


# -

# ### RecursiveCharacterTextSplitter 
# Utility function in LangChain  for splitting large chunks of text into smaller more manageable pieces while ensuring minimal overlap or fragmentation of meaningful content.
#
# ### Key Features
# 1. **Recursive Splitting**: 
#    - It splits the text hierarchically using multiple delimiters. The splitting process starts with the most significant delimiter (e.g., paragraph breaks) and progressively moves to less significant ones (e.g., sentence breaks, word breaks).
#    - This ensures that the text is split cleanly and logically, retaining semantic coherence as much as possible.
#
# 2. **Customizable Delimiters**:
#    - You can specify a list of delimiters (e.g., `\n\n`, `. `, `, `) for the splitting process.
#    - The splitter uses these in order, falling back to smaller units if a larger split would result in chunks exceeding the maximum size.
#
# 3. **Chunk Size and Overlap**:
#    - `chunk_size`: The maximum length of each text chunk, typically measured in characters.
#    - `chunk_overlap`: The number of characters to overlap between consecutive chunks. This helps in preserving context when chunks are processed individually.
#
# 4. **Text Preprocessing**:
#    - Trims unnecessary whitespace around chunks.
#    - Ensures no chunk exceeds the defined `chunk_size`.
#

# +
def list_markdown_files(directory):
    return list(glob.glob(f"{directory}/*.md"))

# Directory containing Markdown files
directory = "../docs"

# List Markdown files
markdown_files = list_markdown_files(directory)

# Parse Markdown files into LangChain documents
documents = parse_markdown_files(markdown_files)

# Split long documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_documents = text_splitter.split_documents(documents)

# Print sample chunked documents
for doc in split_documents[:5]:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content}\n")
# -

# ### VECTOR STORES
#
# #### FAISS (Facebook AI Similarity Search) 
# It is a library designed for efficient similarity search and clustering of dense vectors. In LangChain, FAISS is commonly used as a vector store to store and retrieve embeddings, which are vector representations of text or other data.
#
# #### Key Features of FAISS Vector Stores:
# 1. Efficient Storage and Search: FAISS stores dense vector embeddings and allows fast retrieval using similarity metrics like cosine similarity or inner product.
# 2. Indexing Options: Supports different types of indexes (e.g., Flat, IVF, HNSW) to balance between accuracy and speed depending on the dataset size and search requirements.

# +
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Embed and store split_documents
vector_store = FAISS.from_documents(split_documents, embeddings)

retriever = vector_store.as_retriever()

# +
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Create the QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=True
)


# +
# User's question
query = "What are the guidelines on creating new project"

# Get the answer and source documents
result = qa_chain({"query": query})

# Print the answer
print("Answer:")
print(result['result'])

# Print the source file references
print("\nSource Documents:")
for doc in result['source_documents']:
    print(f"File: {doc.metadata['source']}")
    print(f"Excerpt: {doc.page_content[:200]}...")


# +
# Retrieve vectors by document name
def get_vectors_by_document_name(vector_store, document_name):
    # Query using the metadata field `source`
    results = vector_store.similarity_search(
        query="",  # Pass an empty query or a dummy vector if supported
        k=None,    # Retrieve all matching documents
        filter={"source": document_name}  # Filter by the document name
    )
    return results

# Example usage
document_name = "all.how_write_tutorials.how_to_guide.md"
results = get_vectors_by_document_name(vector_store, document_name)

# Print results
for doc in results:
    print(f"File: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:200]}...")
# -

# ### Demo to create a documentation QA bot but the docs can be updated or deleted.

vector_store = None
folder = "../docs"
filename_to_md5sum = {}

import helpers.hsystem as hsystem
# Function to parse and structure Markdown files. 
def parse_markdown_files(file_paths):
    documents = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        md5sum, _ = hsystem.system_to_string(f"md5sum {file_path}")[1].split()
        filename_to_md5sum[file_path] = md5sum
        # Create a Document object for each file
        documents.append(Document(page_content=content, metadata={"source": file_path}))
    return documents


# +
from langchain.vectorstores import Chroma

def create_vector_store_from_markdown_files(folder):
    # List Markdown files
    markdown_files = list_markdown_files(directory)
    # Parse Markdown files into LangChain documents
    documents = parse_markdown_files(markdown_files)
    # Split long documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(documents)
    # Create embeddings for all documents.
    vector_store = Chroma.from_documents(split_documents, embeddings)
    return vector_store


# -

def get_changes_in_documents_folder(folder):
    # List Markdown files
    markdown_files = list_markdown_files(folder)
    changes = {}
    changes["modified"] = []
    for file_path in markdown_files:
        md5sum, _ = hsystem.system_to_string(f"md5sum {file_path}")[1].split()
        if file_path not in filename_to_md5sum or filename_to_md5sum[file_path] == md5sum:
            print(f"Found a new / modified file {file_path}")
            changes["modified"].append(file_path)
    return changes


def update_files_in_vector_store(vector_store, files):
    if len(files) == 0:
        print("No new files found")
        return
    ids_to_delete = []
    for file in files:
        for doc in vector_store:
            if doc.metadata.get('source') == file:
                ids_to_delete.append(doc.id)
    vector_store.delete(ids_to_delete)
    documents = parse_markdown_files(files)
    # Split long documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(documents)
    texts = [doc.page_content for doc in split_documents]
    embeddings_list = embeddings.embed_documents(texts)  # Compute embeddings for multiple documents
    # Add documents to vector store with computed embeddings
    vector_store.add_documents(
        documents=split_documents,
        embeddings=embeddings_list
    )
    return vector_store


query = "What are the goals for tutorial project?"

if vector_store:
    changes = get_changes_in_documents_folder(folder)
    vector_store = update_files_in_vector_store(vector_store, changes["modified"])
else:
    vector_store = create_vector_store_from_markdown_files(folder)
    

# Create the QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=True
)

# +
# Get the answer and source documents
result = qa_chain({"query": query})

# Print the answer
print("Answer:")
print(result['result'])

# Print the source file references
print("\nSource Documents:")
for doc in result['source_documents']:
    print(f"File: {doc.metadata['source']}")
    print(f"Excerpt: {doc.page_content[:200]}...")
# -




