from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.core import StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from unstructured.partition.pdf import partition_pdf
import mimetypes
import os
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
import pandas as pd

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


class iPdfRAG():
    def __init__(self) -> None:
        db = chromadb.PersistentClient(path="./chroma_db")
        self.chroma_collection = db.get_or_create_collection("iPdf")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

        # MONGO_URI = "mongodb://localhost:27017"
        # self.doc_store = MongoDocumentStore.from_uri(uri=MONGO_URI)
        # self.vector_index_store = MongoIndexStore.from_uri(uri=MONGO_URI)

        self.storage_context = StorageContext.from_defaults(
            # docstore=self.doc_store,
            # index_store=self.vector_index_store,
            vector_store=self.vector_store,
        )

        # self.llm = OpenAI(model="gpt-4o")
        self.llm = Ollama(
            model="llama3.2", temperature=0)

        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
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

        total_nodes = 0
        for filename, file_type in file_types.items():
            filepath= os.path.join(input_dir, filename)
            if file_type == "application/pdf":
                yield f"Processing: {filename}"
                nodes_store[filename] = self._extract2nodes(filepath)
                print(f"{filename} Ingested {len(nodes_store[filename])} Nodes.")
        
        for filename, nodes in nodes_store.items():
            self.vector_index = VectorStoreIndex(
                nodes,
                storage_context=self.storage_context,
                vector_store=self.vector_store
            )
            total_nodes += len(nodes)

        yield f"Completed: Ingested {total_nodes} Nodes from {len(nodes_store)} Files"
        return len(nodes_store)

    def vector_query(self, question:str, top_k=3):
        print(f"question: {question}")
        response = self.vector_index.as_query_engine(similarity_top_k=top_k).query(question)
        print(f"answer: {response}")
        return response
    
    def _extract2nodes(self, filepath):
        # Returns a List[Element] present in the pages of the parsed pdf document
        os.environ["OCR_AGENT"] = "unstructured.partition.utils.ocr_models.paddle_ocr.OCRAgentPaddle"
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
            if len(el_text) > 1:
                print(idx, el_text)
                extra_info = {
                    'file_path': filepath,
                    'filename': el.metadata.filename,
                    'page_number': el.metadata.page_number,
                    'coordinates': str(el.metadata.coordinates.points),
                    'page_width' : el.metadata.coordinates.system.width,
                    'page_height' : el.metadata.coordinates.system.height,
                    'element_idx' : idx,
                    "element_category" : el.category
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

    #return the files path in the chroma library
    def get_filepaths(self)->list:
        files = set()
        docs = self.chroma_collection.get()
        for metadata in docs['metadatas']:
            files.add(metadata['file_path'])
        return list(files)
    
    #return all the nodes by filepath in the chroma library
    def get_documentsbyfilepath(self, filepath:str)->list:
        docs = self.chroma_collection.get(
                            where={"file_path": filepath})
        idxs = []
        for metadata in docs['metadatas']:
            idxs.append(metadata['element_idx'])
        docs_df = pd.DataFrame({
            "idx": idxs,
            "documents": docs['documents']
        })
        return docs_df.sort_values(by='idx')['documents'].tolist()
        
    def ocr_correction(self, chunk: str) -> str:
        
        # Step 1: OCR Correction
        ocr_correction_prompt = f"""Correct OCR-induced errors in the text, ensuring it flows coherently with the previous context. Follow these guidelines:

            1. Fix OCR-induced typos and errors:
            - Correct words split across line breaks
            - Fix common OCR errors (e.g., 'rn' misread as 'm')
            - Use context and common sense to correct errors
            - Only fix clear errors, don't alter the content unnecessarily
            - Do not add extra periods or any unnecessary punctuation

            2. Maintain original structure:
            - Keep all headings and subheadings intact

            3. Preserve original content:
            - Keep all important information from the original text
            - Do not add any new information not present in the original text
            - Remove unnecessary line breaks within sentences or paragraphs
            - Maintain paragraph breaks
            
            4. Maintain coherence:
            - Ensure the content connects smoothly with the previous context
            - Handle text that starts or ends mid-sentence appropriately

            IMPORTANT: Respond ONLY with the corrected text. Preserve all original formatting, including line breaks. Do not include any introduction, explanation, or metadata.

            Current chunk to process:
            {chunk}

            Corrected text:
            """
        
        ocr_corrected_chunk = self.llm.complete(ocr_correction_prompt, max_tokens=len(chunk) + 500)
        
        return ocr_corrected_chunk