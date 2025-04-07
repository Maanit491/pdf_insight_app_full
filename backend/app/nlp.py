import os
from dotenv import load_dotenv
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

if os.environ.get("ENV") != "production":
    load_dotenv(override=True)
# print("API Key:", os.getenv("OPENAI_API_KEY"))

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables or .env file.")
os.environ["OPENAI_API_KEY"] = api_key


def initialize_query_engine():
    folder = 'uploaded_files'
    
    if not os.listdir(folder):
        print("No files found in the uploaded_files directory for NLP model initialization")
        return None

    try:
        documents = SimpleDirectoryReader(folder).load_data()
        index = VectorStoreIndex.from_documents(documents, show_progress=True)
        
        retriever = VectorIndexRetriever(index=index, similarity_top_k=4)
        postprocessor = SimilarityPostprocessor(similarity_cutoff=0.70)
        
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            node_postprocessors=[postprocessor]
        )
        print("NLP model initialized successfully")
        return query_engine
    except Exception as e:
        print(f"Error initializing NLP model: {e}")
        return None


# print(response)
# print(type  (response))
# a=str(response)
# print(a)
# print(type(a))
