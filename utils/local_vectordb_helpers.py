import os
from langchain_ollama import OllamaEmbeddings
import zipfile
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from lxml import etree
import chromadb
from dotenv import load_dotenv

CHROMA_DIR = "./chroma_db"                
COLLECTION_NAME = "knowledge_base"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NSMAP = {'w': WORD_NS}

load_dotenv()

embedding_model = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), temperature=0.0)
ref_folder = os.getenv("DOCUMENT_FOLDER")
ref_file = os.getenv("DOCUMENT_GUIDE")
file_path = os.path.join(ref_folder,ref_file)

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
)

def local_load_knowledge_base(file_path=file_path):
    footnotes = extract_footnotes(file_path)
    docs = extract_body(file_path, footnotes)
    chunks = chunk_documents(docs)
    vector_store = load_or_create_vector_store(chunks)
    return vector_store


def read_xml_from_docx(docx_path: str, part: str) -> bytes:
    """
    Read a specific part (e.g., 'word/document.xml', 'word/footnotes.xml') from the .docx zip.
    Returns bytes or None if not present.
    """
    with zipfile.ZipFile(docx_path) as z:
        if part not in z.namelist():
            return None
        return z.read(part)

def extract_footnotes(docx_path: str):
    """
    Parse word/footnotes.xml and return dict mapping footnote-id -> text.
    """
    xml_bytes = read_xml_from_docx(docx_path, 'word/footnotes.xml')
    if not xml_bytes:
        return {}
    root = etree.fromstring(xml_bytes)
    footnotes = {}
    
    for footnote in root.findall('.//w:footnote', namespaces=NSMAP):
        fid = footnote.get(f'{{{WORD_NS}}}id')
        # collect text runs inside the footnote
        texts = footnote.findall('.//w:t', namespaces=NSMAP)
        text = ''.join([t.text or '' for t in texts])
        if not text:
            continue
        if fid:
            footnotes[fid] = text
    return footnotes

def extract_body(docx_path, footnotes):
    xml_bytes = read_xml_from_docx(docx_path, 'word/document.xml')
    if not xml_bytes:
        return []
    root = etree.fromstring(xml_bytes)
    elements = []

    for index, element in enumerate(root.findall('./w:body/*', namespaces=NSMAP)):
        tag = etree.QName(element.tag).localname if isinstance(element.tag, str) else None
        if tag == 'p':  # paragraph
            elements.append(extract_paragraph(index, element, footnotes))
        elif tag == 'tbl':  # table
            elements.append(extract_table(index, element, footnotes))
    return elements

def extract_paragraph(index, element, footnotes):
    """
    Parse word/document.xml and return list of paragraphs with footnote markers replaced by
    a textual marker like [fn:ID]. This ensures we retain exact references.
    Each paragraph dict: {"index": int, "text": str, "style": <style_name or None>}
    """
    text = form_text(element, footnotes)
    
    # identify style if present (w:pPr/w:pStyle/@w:val)
    style = None
    pPr = element.find('w:pPr', namespaces=NSMAP)
    if pPr is not None:
        pStyle = pPr.find('w:pStyle', namespaces=NSMAP)
        if pStyle is not None:
            style = pStyle.get(f'{{{WORD_NS}}}val')

    return {"index": index, "text": text, "style": style}


def extract_table(index, element, footnotes):
    table_data = []

    rows = element.findall('w:tr', namespaces=NSMAP)
    for row in rows:
        row_data = []
        cells = row.findall('w:tc', namespaces=NSMAP)
        for cell in cells:
            cell_text = ""
            paragraphs = cell.findall('w:p', namespaces=NSMAP)
            
            for para in paragraphs:
                para_text = ""
                para_text += form_text(para, footnotes)
                cell_text += para_text

            row_data.append(cell_text)

        table_data.append(row_data)

    markdown_table = convert_table_to_markdown(table_data)
    return {"index": index, "text": markdown_table, "style": "Table"}

def form_text(element, footnotes):
    # text is concatenation of w:t nodes, but we must handle w:footnoteReference specially
    text = ""

    # Add bullet point if it's a list item
    pStyle = element.find('.//w:pStyle', namespaces=NSMAP)
    if pStyle is not None:
        style_val = pStyle.get(f'{{{WORD_NS}}}val')
        if style_val == "ListBullet" or style_val == "ListParagraph":
            text += "• "

    # iterate through child nodes in order to preserve sequence
    for child in element.iter():
        tag = etree.QName(child.tag).localname if isinstance(child.tag, str) else None
        if tag == 't':  # text node
            if child.text:
                text += child.text
        elif tag == 'footnoteReference':
            # footnote ref appears: add footnote
            fid = child.get(f'{{{WORD_NS}}}id')
            if fid:
                footnote_text = footnotes.get(fid, "")
                text += f" [footnote {fid}: {footnote_text}]"
    text = text.strip()
    text += "\n"
    return text
                
def convert_table_to_markdown(table_data):
    """
    Convert 2D list of table data into simple markdown table string.
    """
    headers = table_data.pop(0)
    result = ""
    result += "| " + " | ".join(headers) + " |\n"
    result += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in table_data:
        result += "| " + " | ".join(row) + " |\n"
    return result


def chunk_documents(paragraphs):
    chunks = []

    section = ""
    currentChunk = Document("", metadata={"source": ref_file})
    isTablePrevious = False
    for i in range(len(paragraphs)):
        paragraph = paragraphs[i]
        style = paragraph.get("style")
        text = paragraph.get("text")
        if not text:
            continue
        
        if style == "Heading2":
            # Split by Heading2 as it separates sections, this is specific to current document.
            if section and currentChunk.page_content:
                chunks.append(currentChunk)
                currentChunk = Document("", metadata={"source": ref_file})
            section = text
        elif style == "Table":
            # Assume table title is previous line, this is specific to current document.
            table_title = paragraphs[i-1]["text"] if i > 0 else ""
            if currentChunk.page_content:
                chunks.append(currentChunk)
                currentChunk = Document("", metadata={"source": ref_file, "table": table_title})
            currentChunk.page_content += table_title
            isTablePrevious = True
        elif isTablePrevious:
            isTablePrevious = False
            chunks.append(currentChunk)
            currentChunk = Document("", metadata={"source": ref_file})

        currentChunk.metadata["section"] = section
        currentChunk.page_content += text
    if currentChunk.page_content:
        chunks.append(currentChunk)
    
    final_chunks = []
    for chunk in chunks:
        if not chunk.metadata.get("table"):
            l_chunks = text_splitter.split_documents([chunk])
            final_chunks.extend(l_chunks)
        else:
            final_chunks.append(chunk)

    # see if nicer markdown or spliting tables further helps, or not splitting further
    # print("Chunks:\n")
    # print(final_chunks)
    return final_chunks

def load_or_create_vector_store(documents, embedder=embedding_model, persist_directory=CHROMA_DIR, collection_name=COLLECTION_NAME):
    """
    Return a LangChain Chroma vector_store for the given persisted collection.
    - If the collection exists on disk, instantiate and return the LangChain Chroma wrapper.
    - If the collection is missing and 'documents' is provided, create it via Chroma.from_documents and return that vector_store.
    """
    os.makedirs(persist_directory, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_directory)

    # collection exists -> return LangChain wrapper pointing at the persisted collection
    try:
        client.get_collection(name=collection_name)
        vector_store = Chroma(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_function=embedder
        )
        return vector_store
    except Exception as e:
        # collection missing, create and persist using LangChain helper (computes embeddings)
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embedder,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        return vector_store

# output_filename="documents.txt"
# output_file= os.path.join(ref_folder,output_filename)

# def print_documents_to_file(documents, output_file=output_file):
#     # This function prints the documents to a file for debugging purposes.
#     # Clear and then write to output file to see chunks
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.truncate(0)  # Clear the file

#     for i in range(len(documents)):
#         doc = documents[i]
#         with open(output_file, "a", encoding="utf-8") as f:
#             f.write(f"Chunk {i+1}: \n")
#             f.write(f"Page Content: {doc.page_content}\n")
#             f.write(f"Metadata: {doc.metadata}\n")
#             f.write("\n\n")
