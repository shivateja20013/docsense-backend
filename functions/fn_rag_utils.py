import os
import chromadb
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, OpenAIEmbedding
from llama_index.extractors import QuestionsAnsweredExtractor
from llama_index.ingestion import IngestionPipeline
from llama_index.llms import OpenAI
from llama_index.node_parser import SentenceSplitter
from llama_index.schema import MetadataMode
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

# Define chunk parameters
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP'))

INDEX_PATH = os.getenv("INDEX_PATH")
FILES_PATH = os.getenv("FILES_PATH")

llm = OpenAI(model=LLM_MODEL, temperature=0.0)
embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL, embed_batch_size=1)

async def index_files(chat_id: int):
    FILES_DIR = os.path.join(FILES_PATH, str(chat_id))
    
    # Create ChromaDB client and vector store for data
    data_db = chromadb.PersistentClient(path=INDEX_PATH)
    data_collection = data_db.get_or_create_collection('index_' + str(chat_id), metadata={"hnsw:space": "cosine"})
    data_vector_store = ChromaVectorStore(chroma_collection=data_collection)

    # Set storage and service contexts for data
    data_storage_context = StorageContext.from_defaults(vector_store=data_vector_store)
    data_service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    # Read documents from a directory and extract nodes
    documents = SimpleDirectoryReader(FILES_DIR).load_data()
    node_parser = SentenceSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    
    # QuestionsAnsweredExtractor is used to add questions that can be answered by the chunk of data to help embeddings for better retrieval from index
    # extractors = [
    #     QuestionsAnsweredExtractor(
    #         questions=10, llm=llm, metadata_mode=MetadataMode.EMBED
    #     ),
    # ]
    normal_nodes = node_parser.get_nodes_from_documents(documents=documents)
    pipeline = IngestionPipeline(transformations=[node_parser])
    extracted_nodes = pipeline.run(nodes=normal_nodes, in_place=False, show_progress=True)
    
    # Create a VectorStoreIndex from extracted nodes
    data_index = VectorStoreIndex(nodes=extracted_nodes, storage_context=data_storage_context, service_context=data_service_context, show_progress=True)
    return data_index


async def getIndex(chat_id: int):
    # Create ChromaDB client and vector store for data
    data_db = chromadb.PersistentClient(path=INDEX_PATH)
    data_collection = data_db.get_or_create_collection('index_' + str(chat_id), metadata={"hnsw:space": "cosine"})
    data_vector_store = ChromaVectorStore(chroma_collection=data_collection)

    # Set storage and service contexts for data
    data_storage_context = StorageContext.from_defaults(vector_store=data_vector_store)
    data_service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    data_index = VectorStoreIndex.from_vector_store(vector_store=data_vector_store, storage_context=data_storage_context, service_context=data_service_context)
    return data_index