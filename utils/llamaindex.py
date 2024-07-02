
# 向量数据库: Elasticsearch

# from llama_index.vector_stores.elasticsearch import ElasticsearchStore
# from llama_index.vector_stores.elasticsearch import AsyncDenseVectorStrategy

from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.core import StorageContext

from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

class llamaindex_base():
    vector_store = None
    embed_model = None
    doc_store = None
    index_store = None
    storage_context = None
    index = None
    query_engine = None
    
    def __init__(self) -> None:
        # ES_URI = "http://localhost:9200"
        # self.vector_store = ElasticsearchStore(
        #     es_url=ES_URI,
        #     index_name="my_index",
        #     retrieval_strategy=AsyncDenseVectorStrategy(hybrid=True), # 使用混合检索
        # )
        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_or_create_collection("chemical")
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        MONGO_URI = "mongodb://localhost:27017"
        self.doc_store = MongoDocumentStore.from_uri(uri=MONGO_URI)
        self.index_store = MongoIndexStore.from_uri(uri=MONGO_URI)

        self.storage_context = StorageContext.from_defaults(
            docstore=self.doc_store,
            index_store=self.index_store,
            vector_store=self.vector_store,
        )

        llm = Gemini(model="models/gemini-1.5-flash",
                    safety_settings={
                                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                },)
        # service_context = ServiceContext.from_defaults(llm=llm, temperature=0.5, system_prompt="You are an expert on code documentation and your job is to answer technical questions. Assume that all questions are related to the code shared in context. Keep your answers technical and based on facts – do not hallucinate features.")

        # 本地嵌入模型: bge-base-en-v1.5
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        # LlamaIndex全局配置
        Settings.llm = llm
        Settings.embed_model = self.embed_model
        self.index = VectorStoreIndex.from_vector_store(
                            storage_context=self.storage_context,
                            vector_store= self.vector_store,
                            # service_context=service_context,
                        )

    def load(self, input_dir="./storage"):
        # load the pdfs into llamaindex database/vectorbase
        # return the numbers of docs load.
        # 加载文件信息: SimpleDirectoryReader
        documents = SimpleDirectoryReader(input_dir=input_dir, recursive=True).load_data() 
        print(f"Loaded {len(documents)} Files")

        sentence_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

        # 数据转换管道,防止重复导入

        pipeline = IngestionPipeline(
            transformations=[
                sentence_splitter,
                self.embed_model,
            ],
            docstore=self.doc_store,
            vector_store=self.vector_store,
        )

        # 生成索引存入向量数据库
        nodes = pipeline.run(documents=documents)
        print(f"Ingested {len(nodes)} Nodes")
        # 创建向量存储索引
        # self.index = VectorStoreIndex(nodes, storage_context=self.storage_context)
        # 3. Update the index (this step is crucial)
        self.index = VectorStoreIndex.from_vector_store(
            storage_context=self.storage_context,
            vector_store=self.vector_store
        )
        # 创建查询引擎并查询
        return len(nodes)

    def query(self, question:str):
        print(f"question: {question}")
        response = self.index.as_query_engine(top_k=3).query(question)
        print(f"answer: {response}")
        return response

