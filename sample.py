# Importing necessary libraries and modules
import csv
import logging
import os
import pickle


import chromadb
import tiktoken
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, OpenAIEmbedding, Document
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.chat_engine.types import ChatMode
from llama_index.extractors import QuestionsAnsweredExtractor
from llama_index.indices.vector_store import VectorIndexRetriever
from llama_index.ingestion import IngestionPipeline
from llama_index.llms import OpenAI
from llama_index.node_parser import SentenceSplitter
from llama_index.schema import MetadataMode
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore

# Importing custom modules
import chat_history  # to handle chat history

# Creating a table for storing chat history
chat_history.create_table()

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Define chunk parameters
chunk_size = 512
chunk_overlap = 64

# Set conversation-related parameters for passing chat history to chat engine
conversation_id = "conversation_1"
no_of_conversations = 2

# Set chat mode
chat_mode = ChatMode.REACT
trial = "B"  # Used to record the logs and results distinctly for analysis and testing purposes

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[
                        # logging.StreamHandler(stream=sys.stdout),
                        # logging.FileHandler('./logs/index_'+str(chunk_size)+'_'+str(chunk_overlap)+'_qae20_text-embedding-ada-002_cosine.txt'),
                        # logging.FileHandler('./logs/'+chat_mode+'_'+str(chunk_size)+'_'+str(chunk_overlap)+'_qae20_text-embedding-ada-002_cosine'+trial+'.txt')
                    ])
logger = logging.getLogger()

# Token counting handler for tracking usage
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo-1106").encode,
    verbose=False,  # set to true to see usage printed to the console
)
callback_manager = CallbackManager([token_counter])

# Initialize llm and embeddings models
llm = OpenAI(model="gpt-3.5-turbo-1106", temperature=0.0)
embed_model = OpenAIEmbedding(model="text-embedding-ada-002", embed_batch_size=1)

# Creating ChromaDB client and vector store for data
data_db = chromadb.PersistentClient(
    path='./index_' + str(chunk_size) + '_' + str(chunk_overlap) + '_qae20_text-embedding-ada-002_cosine')
data_collection = data_db.get_or_create_collection(
    'index_' + str(chunk_size) + '_' + str(chunk_overlap) + '_qae20_text-embedding-ada-002_cosine',
    metadata={"hnsw:space": "cosine"})
data_vector_store = ChromaVectorStore(chroma_collection=data_collection)

# Setting storage and service contexts for data
data_storage_context = StorageContext.from_defaults(vector_store=data_vector_store)

data_service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model, chunk_size=chunk_size,
                                                    chunk_overlap=chunk_overlap, callback_manager=callback_manager)

# # One time step
# # Creating index from documents - start
#
# Reading documents from a directory and extracting nodes
#
# documents = SimpleDirectoryReader("../pdfs").load_data()
# node_parser = SentenceSplitter(
#     chunk_size=chunk_size, chunk_overlap=chunk_overlap
# )
#
# # QuestionsAnsweredExtractor is being used to add questions that can be answered by the chunk of data to help embeddings for better retrival from index
# extractors = [
#     QuestionsAnsweredExtractor(
#         questions=20, llm=llm, metadata_mode=MetadataMode.EMBED
#     ),
# ]
# normal_nodes = node_parser.get_nodes_from_documents(documents=documents)
# pipeline = IngestionPipeline(transformations=[node_parser, *extractors])
# extracted_nodes = pipeline.run(nodes=normal_nodes, in_place=False, show_progress=True)
#
# # Saving the extracted nodes to a file
# with open('extracted_nodes_2048_128_qae20.pkl', 'wb') as file:
#     pickle.dump(extracted_nodes, file)
#
# # Creating a VectorStoreIndex from extracted nodes
# data_index = VectorStoreIndex(nodes=extracted_nodes, storage_context=data_storage_context, service_context=data_service_context, show_progress=True)
# # Creating index from documents - end

# Initialize vector store index for questions
questions_db = chromadb.PersistentClient(path='./questions_128_0_text-embedding-ada-002_cosine')
questions_collection = questions_db.get_or_create_collection('questions_128_0_text-embedding-ada-002_cosine',
                                                             metadata={"hnsw:space": "cosine"})
questions_vector_store = ChromaVectorStore(chroma_collection=questions_collection)

# Setting up storage and service contexts for questions
questions_storage_context = StorageContext.from_defaults(vector_store=questions_vector_store)

questions_service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model, chunk_size=128,
                                                         chunk_overlap=12, callback_manager=callback_manager)

# List of questions for testing
questions = [
    "What was the total revenue of Microsoft in 2021?",
    "What about 2022?",
    "What steps did Microsoft take in fiscal year 2020 to address its carbon footprint?",
    "How many people were employed by Microsoft as of June 30, 2021, and what is the distribution across different services?",
    "What was the total revenue of Tesla in 2021?",
    "What about 2022?",
    "How many registered holders of record did Microsoft have for its common stock on July 25, 2022, and under which symbol is its common stock traded on the NASDAQ Stock Market?",
    "What achievements highlight the diversity of Microsoft's work in fiscal year 2021?",
    "What are the properties or manufacturing facilities owned or leased by Tesla in 2021, and where are they located?",
    "What was the total revenue of Tesla in 2022?",
    "How many Tesla vehicles were produced and delivered in 2021?",
    "What about 2022?",
    "What was the total worth of Tesla's assets in 2021 according to the Consolidated Balance Sheet?",
    "What loss did the company incur during the year ended December 31, 2019, related to closing operations in certain facilities?"
]

# Loading and initializing data index from Vector Store DB
data_index = VectorStoreIndex.from_vector_store(vector_store=data_vector_store, storage_context=data_storage_context,
                                                service_context=data_service_context)

# System prompt for chat interactions
system_prompt = '''You're a senior financial Analyst. Your answers should only be from the documents provided. Do not use your own information. Ensure that you check the documents thoroughly to ensure you have not missed any information that is useful. If required, recheck by rewording the query.
When providing the response first summarize the source document locator information in the form "source_docs:[{document, page|location},...]"  and then provide the answer.'''

# Open CSV file for writing results
with open('./results/' + chat_mode + '_' + str(chunk_size) + '_' + str(
        chunk_overlap) + '_qae20_text-embedding-ada-002_cosine_' + trial + '.csv', mode='w', newline='') as file:
    csv_writer = csv.writer(file)

    # BaseChatEngine
    chat_engine = data_index.as_chat_engine(chat_mode=chat_mode, system_prompt=system_prompt)

    # Loop through each question
    for question in questions:
        # Loop through each question
        history = chat_history.fetch_chat_history(conversation_id, no_of_conversations, condensed_query=False)

        # Initialize vector store index for questions
        questions_index = VectorStoreIndex.from_vector_store(vector_store=questions_vector_store,
                                                             storage_context=questions_storage_context,
                                                             service_context=questions_service_context)

        # Retrieve similar questions from the questions vector store
        questions_retriever = VectorIndexRetriever(index=questions_index, similarity_top_k=5)
        retrieved_questions = questions_retriever.retrieve(question)
        retrieved_questions_str = ""
        for retrieved_question in retrieved_questions:
            retrieved_questions_str += retrieved_question.get_text() + "\t" + str(retrieved_question.get_score()) + "\n"

        # Generate response for the given question
        response = chat_engine.chat(message=question, chat_history=history)
        # Fetching the condensed question from the response object
        condensed_question = response.sources[-1].raw_input.get('input')

        # Add the chat history for the current question
        chat_history.add_chat_history(conversation_id, question, str(condensed_question), str(response))

        # Print and write results to CSV
        print("\nQuestion: ", question, "\nCondensed Question: ", condensed_question, "\nResponse: ", response, "\nRetrieved Questions: \n", retrieved_questions_str)
        csv_writer.writerow([question, condensed_question, response, retrieved_questions_str])

        # Retrieve similar questions for the condensed question
        retrieved_questions = questions_retriever.retrieve(condensed_question)
        # If needed, update the questions index with the condensed question
        if len(retrieved_questions) > 0 and retrieved_questions[0].get_score() < 0.95:
            question_docs = [Document(text=str(condensed_question))]
            questions_index = VectorStoreIndex.from_documents(question_docs, questions_storage_context, questions_service_context, show_progress=True)
