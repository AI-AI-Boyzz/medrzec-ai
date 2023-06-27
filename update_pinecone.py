import os
import sys

import dotenv
import pinecone
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone

INDEX_NAME = "playbook"

dotenv.load_dotenv()

pinecone.init(os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"])


print("Clearing DB index…")
pinecone.Index(INDEX_NAME).delete(delete_all=True)

print("Splitting the document…")
documents = TextLoader(
    " ".join(sys.argv[1:]),
    encoding="utf8",
).load_and_split(CharacterTextSplitter(chunk_size=256, chunk_overlap=0))


print("Uploading chunks…")
Pinecone.from_documents(
    documents,
    OpenAIEmbeddings(),  # pyright: ignore [reportGeneralTypeIssues]
    index_name=INDEX_NAME,
)

print("Success!")
