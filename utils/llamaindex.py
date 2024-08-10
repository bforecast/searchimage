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
from llama_index.core import VectorStoreIndex, ServiceContext, SummaryIndex, DocumentSummaryIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from unstructured.partition.pdf import partition_pdf
import mimetypes
import os
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import IndexNode

from llama_index.llms.ollama import Ollama

def get_files_with_type(directory):
  """
  Returns a dictionary containing file names and their MIME types.

  Args:
    directory: The path to the directory to search.

  Returns:
    A dictionary where keys are file names and values are MIME types.
  """
  files_with_types = {}
  for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
      mime_type = mimetypes.guess_type(filepath)[0]
      files_with_types[filename] = mime_type
  return files_with_types

class llamaindex_base():
    vector_store = None
    embed_model = None
    doc_store = None
    index_store = None
    storage_context = None
    vector_index = None
    doc_summary_index = None
    query_engine = None
    
    def __init__(self) -> None:
        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_or_create_collection("chemical")
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        MONGO_URI = "mongodb://localhost:27017"
        self.doc_store = MongoDocumentStore.from_uri(uri=MONGO_URI)
        self.vector_index_store = MongoIndexStore.from_uri(uri=MONGO_URI)

        self.storage_context = StorageContext.from_defaults(
            docstore=self.doc_store,
            index_store=self.vector_index_store,
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
        self.vector_index = VectorStoreIndex.from_vector_store(
                            storage_context=self.storage_context,
                            vector_store=self.vector_store
                        )

    def load(self, input_dir="./storage/pdf"):
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
        # 3. Update the index (this step is crucial)
        self.vector_index = VectorStoreIndex.from_vector_store(
            storage_context=self.storage_context,
            vector_store=self.vector_store
        )
        return len(nodes)

    def vector_query(self, question:str):
        print(f"question: {question}")
        response = self.vector_index.as_query_engine(top_k=3).query(question)
        print(f"answer: {response}")
        return response
    
    def document_summary_query(self, question:str):
        print(f"question: {question}")
        response = self.doc_summary_index.as_query_engine(response_mode="tree_summarize", use_async=True).query(question)
        print(f"answer: {response}")
        return response

class iPdfRAG():
    vector_store = None
    embed_model = None
    doc_store = None
    index_store = None
    storage_context = None
    vector_index = None
    doc_summary_index = None
    query_engine = None
    llm = None
    
    def __init__(self) -> None:
        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_or_create_collection("iPdf")
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        MONGO_URI = "mongodb://localhost:27017"
        self.doc_store = MongoDocumentStore.from_uri(uri=MONGO_URI)
        self.vector_index_store = MongoIndexStore.from_uri(uri=MONGO_URI)

        self.storage_context = StorageContext.from_defaults(
            docstore=self.doc_store,
            index_store=self.vector_index_store,
            vector_store=self.vector_store,
        )

        self.llm = OpenAI(model="gpt-4o")
        # self.llm = Ollama(model="qwen2:1.5b", request_timeout=600.0)

        # service_context = ServiceContext.from_defaults(llm=llm, temperature=0.5, system_prompt="You are an expert on code documentation and your job is to answer technical questions. Assume that all questions are related to the code shared in context. Keep your answers technical and based on facts – do not hallucinate features.")

        # 本地嵌入模型: bge-base-en-v1.5
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        # LlamaIndex全局配置
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        self.vector_index = VectorStoreIndex.from_vector_store(
                            storage_context=self.storage_context,
                            vector_store=self.vector_store
                        )

    def load(self, input_dir="./img_pdf"):
        # load the pdfs into llamaindex database/vectorbase
        # return the numbers of docs load.
        nodes_store = {}
        file_types = get_files_with_type(input_dir)

        for filename, file_type in file_types.items():
            filepath= os.path.join(input_dir, filename)
            if file_type == "application/pdf":
                nodes_store[filename] = self._extract2nodes(filepath)
                print(f"{filename} Ingested {len(nodes_store[filename])} Nodes.")
        
        # Build agents dictionary
        agents = {}
        for filename, nodes in nodes_store.items():
            # build vector index
            vector_index = VectorStoreIndex(
                                nodes,
                                storage_context=self.storage_context,
                                vector_store=self.vector_store
                            )
            # build summary index
            summary_index = SummaryIndex(
                                nodes,
                                storage_context=self.storage_context,
                            )
            # define query engines
            vector_query_engine = vector_index.as_query_engine()
            list_query_engine = summary_index.as_query_engine()
            # define tools
            query_engine_tools = [
                QueryEngineTool(
                    query_engine=vector_query_engine,
                    metadata=ToolMetadata(
                        name="vector_tool",
                        description=(
                            f"Useful for retrieving specific context from {filename}"
                        ),
                    ),
                ),
                QueryEngineTool(
                    query_engine=list_query_engine,
                    metadata=ToolMetadata(
                        name="summary_tool",
                        description=(
                            "Useful for summarization questions related to"
                            f" {filename}"
                        ),
                    ),
                ),
            ]
            # build agent
            agent = OpenAIAgent.from_tools(
                query_engine_tools,
                llm=self.llm,
                verbose=True,
            )
            agents[filename] = agent
        
        #Build Composable Retriever over these Agents
        # define top-level nodes
        objects = []
        for filename, agent in agents.items():
            # define index node that links to these agents
            file_summary = (
                f"This content contains information about {filename}. Use"
                " this index if you need to lookup specific facts about"
                f" {filename}.\nDo not use this index if you want to analyze"
                " multiple products."
            )
            node = IndexNode(
                text=file_summary, index_id=filename, obj=agents[filename]
            )
            objects.append(node)
        # define top-level retriever
        self.vector_index = VectorStoreIndex(
                                    objects=objects,
                                    storage_context=self.storage_context,
                                    vector_store=self.vector_store
                                )
        query_engine = vector_index.as_query_engine(similarity_top_k=1, verbose=True)
        
        # should use Seattle agent -> summary tool
        response = query_engine.query(
            "Give me a summary on all the risks of CP-2000W"
        )
        print(response)
        return len(nodes_store)

    def vector_query(self, question:str, top_k=3):
        print(f"question: {question}")
        response = self.vector_index.as_query_engine(similarity_top_k=top_k).query(question)
        print(f"answer: {response}")
        return response
    
    def document_summary_query(self, question:str):
        print(f"question: {question}")
        response = self.doc_summary_index.as_query_engine(response_mode="tree_summarize", use_async=True).query(question)
        print(f"answer: {response}")
        return response
    
    def _extract2nodes(self, filepath):
        # Returns a List[Element] present in the pages of the parsed pdf document
        os.environ["OCR_AGENT"] = "paddle"
        elements = partition_pdf(filepath, 
                         infer_table_structure=True,
                         include_page_breaks=True, 
                         strategy='hi_res',
                         hi_res_model_name="yolox_quantized",
                         languages=["eng"])
        page_number = 1
        nodes = []
        preNode:TextNode = None
        preText = ""
        nodeLevel = 0
        parentNodes = [None, None, None]
        for idx, el in enumerate(elements):
            isSection = False
            if el.category == "PageBreak":
                page_number += 1
                continue
            elif el.category == "Image":
                continue
            elif el.category == "Table":
                el_text = el.text
                if el.metadata.text_as_html:
                    el_text = el.metadata.text_as_html
                isSection = el.text.lower().startswith('section')

            else:
                if len(el.text) > 0:
                    isSection = el.text.lower().startswith('section')

                    el_text = preText + el.text
                    # skip "Page 1" string
                    if el_text.lower().startswith('page'):
                        continue
                    if el_text[-1] == ":":
                        preText = el_text + " "
                        continue
                    preText = ""
                else:
                    continue
            
            # append to the nodes
            if len(el_text) > 16:
                print(idx, el_text)
                extra_info = {
                    'file_path': filepath,
                    'filename': el.metadata.filename,
                    'page_number': el.metadata.page_number,
                    'coordinates': str(el.metadata.coordinates.points),
                    'page_width' : el.metadata.coordinates.system.width,
                    'page_height' : el.metadata.coordinates.system.height,
                }
                new_node = TextNode(text = el_text, extra_info = extra_info)
                if nodeLevel == 0:
                    nodeLevel = 1
                    parentNodes[nodeLevel] = new_node
                else:
                    if isSection:
                        if parentNodes[2]:
                            new_node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=parentNodes[2].node_id)
                            parentNodes[2].relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=new_node.node_id)
                        new_node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(node_id=parentNodes[1].node_id)
                        parentNodes[2] = new_node
                        preNode = None
                        nodeLevel = 2
                    else:
                        if preNode:
                            new_node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=preNode.node_id)
                            preNode.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=new_node.node_id)
                        preNode = new_node
                        new_node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(node_id=parentNodes[nodeLevel].node_id)
                        if nodeLevel == 1 and not parentNodes[2]:
                            parentNodes[2] = new_node
                nodes.append(new_node)
        return nodes


