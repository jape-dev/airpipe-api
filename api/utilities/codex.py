from langchain.vectorstores import Chroma
from langchain.docsore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
embeddings = OpenAIEmbeddings()
import json

# data schema is a JSON payload describing the available tables.
# Get this from the API - is this step necessary if just passing from
# specific channels...probably not.

documents = [
    Document(
        page_conent=f"Table: {table_meta['table']}",
        metadata={
            "schema": table_meta["schema"],
            "table": table_meta["table"],
            "columns": json.dumps(table_meta["columns"])
        },
    )
    for table_meta in data_schema
]  

db = Chroma.from_documents(documents, embedding=embeddings,
                           persist_directory=persist_directory)
