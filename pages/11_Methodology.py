import streamlit as st

from utils.access import check_password


if not check_password():
    st.stop()


st.title("Methodology")

st.header("RAG LLM Core", divider="grey")

st.write("""The core of the application is the data classification guide knowledge base. 
         Both Data Classification Assistant and Q&A assistant access this knowledge base through Retrieval Augmented Generation (RAG) before generating LLM responses to users. """)


st.subheader("1. Document Loading")
st.write("""The Data Classification Guide that forms our knowledge base is a DOCX document with multiple tables and references in the footnotes. 
         This presents some difficulty in document loading, as basic loaders will either miss out or cannot extract the information in the tables and references reliably.""")
st.write("""To preserve the elements of the DOCX document, we decided to use Unstructured's [UnstructuredWordDocumentLoader](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.word_document.UnstructuredWordDocumentLoader.html), 
         a more advanced document loader that splits the document into its constituent elements, 
         such as Title, Text and Table, and includes metadata, such as page number of the element.""")


st.subheader("2. Splitting and Chunking")
st.write("""RecursiveCharacterTextSplitter is used to split the documents, 
         Additionally, before storing the chunks, we made a few augmentations to the chunks to potentially improve the retrieval process and the quality of the retrieved information.""")

st.write("**Augmentation 1: Append Missing References**")
st.write("""UnstructuredWordDocumentLoader does not load the multiple references in the footnotes of the original document. Many of these references contain important guidance on how to classify 
         data. Thus, we separately extracted the references from the document and appended it to the back of the rest of the extracted chunks. A potential improvement for the future will be to 
         embed the exact locations in the document the references are from, to preserve the relevant context of the references.""")

st.write("**Augmentation 2: Convert Tables to Markdown**")
st.write("""UnstructuredWordDocumentLoader returns tables as both plain text and one long html string. In an effort to preserve the table structure for better LLM understanding and embedding, 
         we converted the multiple tables from the original document into markdown before storage. We also merged the titles of the tables with the tables into one chunk, 
         to potentially improve the ability of the retriever to find the relevant tables. """)

st.write("**Augmentation 3:Include Section in Metadata**")
st.write("""To further improve the understanding of the chunks, we appended the section of the original document the chunk is from to their metadata. For example, if a chunk is from the Security 
         Classification Framework (SCF) section of the original document, it might be useful in answering queries about SCF. Thus, we append "section": "SCF Framework" into the chunk's metadata.""")

st.subheader("3. Storage")
st.write("After processing and augmenting the chunks, we generate embeddings with OpenAI's text-embedding-3-small and store them in a Chroma vector database for RAG retrieval.")

st.subheader("4. Retrieval")
st.write("""Once the embeddings are stored in the Chroma vector database, we can retrieve relevant chunks from the vector database based on user queries. 
         The retrieval process is slightly different for Data Classification Assistant and Q&A Assistant.""")

st.write("**Data Classification Assistant**")
st.write("""
         Query rewriting and multi query generation are used to improve the retrieval process, via the following steps:
         
         1. When users input a text/document to classify, the large language model is given the context of the assistant's goal (i.e., data classification) and the user input. 
         2. Based on the context and input, the model is then tasked with coming up with multiple smaller and more focused queries whose answers are required to accurately classify the input. 
         For example, if the input has many account numbers, a smaller, more focused query will be to ask how are account numbers classified. 
         3. These queries are then sent to the retriever for Multi-Query Retrieval to fetch relevant chunks from the vector database.

         By using multiple, more direct queries with more focused semantic meanings instead of the user input for retrieval, we can more effectively retrieve the specific information needed for classification.
         """)

st.write("**Q&A Assistant**")
st.write("""
         1. When users input a question, the large language model is given the context of the assistant's goal (i.e., answering questions about data classification) the user input and the chat history.
         2. With the context, chat history and input, the model reformulates the user's question into a standalone question that is useful enough to retrieve the relevant information to answer the user.
         3. This reformulated question is then sent to the retriever for retrieval from the vector database.

         By reformulating the user's question into a more focused query, we can improve the retrieval of relevant information and provide more accurate answers without diluting the context window with irrelevant details.
         """)

st.subheader("5.Output")
st.write("""
        After retrieving the relevant chunks from the vector database, the next step is to generate a response for the user. This involves the following steps:
""")
st.markdown("""
        1. The retrieved chunks are passed to the large language model along with the original user input and context about the assistant's role and tasks.
        2. The model processes this information and generates a response that addresses the user's input. We have included the following prompting techniques to improve the model's performance: 
            - XML tags: To delineate and better identify different parts of the prompt, helping the model understand the structure and context better.
            - Few shot prompting: To provide the model with examples of desired outputs, helping it understand the format and style of the response.
            - Step-by-step reasoning: To encourage the model to think through the problem and provide a more detailed and accurate response.
            - Generate a structured output: To help the model organize its response clearly and also allow easier extraction of output to display.
        3. Finally, the following information is presented to the user:
            1. Overall combined security and sensitivity classification of the text/document.
            2. The security classification and its reasoning.
            3. The sensitivity classification and its reasoning.
            4. The original text with potentially damaging information in bold.
            5. An extra functionality to anonymise certain PIIs with Govtech's cloak. 
    """)

st.write("Do refer to the provided source code for more information.")

st.subheader("Data Classification Assistant Flowchart")

st.image("data/Data Classification Flowchart.png", caption="Data Classification Assistant Flowchart")

st.subheader("Q&A Assistant Flowchart")

st.image("data/Q&A Flowchart.png", caption="Q&A Assistant Flowchart")
