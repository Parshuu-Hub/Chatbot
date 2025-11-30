import os,tempfile
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from modules.cloudinary_storage import upload_pdf_to_cloudinary


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medicalindex"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
# UPLOAD_DIR = "./uploaded_docs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
existing_indexes = [i["name"] for i in pc.list_indexes()]

# Create or recreate the index with correct dimension (3072 for Gemini embeddings)
if PINECONE_INDEX_NAME in existing_indexes:
    desc = pc.describe_index(PINECONE_INDEX_NAME)
    # Check current dimension and recreate if needed
    current_dim = getattr(desc, "dimension", desc.get("dimension", None))
    if current_dim != 3072:
        print(f"Recreating index '{PINECONE_INDEX_NAME}' with correct dimension 3072...")
        pc.delete_index(PINECONE_INDEX_NAME)
        time.sleep(2)
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=3072,
            metric="cosine",
            spec=spec
        )
else:
    print(f"Creating new index '{PINECONE_INDEX_NAME}' with dimension 3072...")
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=3072,
        metric="dotproduct",
        spec=spec
    )

# Wait until index is ready
while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
    time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)

# load, split, embed and upsert pdf docs content
def load_vectorstore(uploaded_files):
    embed_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    file_urls = []

    for file in uploaded_files:
        # Upload to Cloudinary
        file_bytes = file.file.read()
        public_url = upload_pdf_to_cloudinary(file_bytes, file.filename, file.content_type)
        file_urls.append(public_url)

        # Save temporarily for PyPDFLoader
        temp_pdf = Path("/tmp") / file.filename
        with open(temp_pdf, "wb") as f:
            f.write(file_bytes)

        # Load & split PDF
        loader = PyPDFLoader(str(temp_pdf))
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        texts = [c.page_content for c in chunks]
        metadata = [c.metadata | {"text": c.page_content} for c in chunks]
        ids = [f"{file.filename}-{i}" for i in range(len(chunks))]

        # Embeddings
        print("Generating embeddings...")
        embeddings = embed_model.embed_documents(texts)

        print("Upserting into Pinecone...")
        with tqdm(total=len(embeddings)) as pbar:
            index.upsert(vectors=zip(ids, embeddings, metadata))
            pbar.update(len(embeddings))

        print(f"Completed processing PDF: {file.filename}")

    return file_urls

    # file_paths = []
    
    # 1. upload
    # for file in uploaded_files:
    #     save_path = Path(UPLOAD_DIR) / file.filename
    #     with open(save_path, "wb") as f:
    #         f.write(file.file.read())
    #     file_paths.append(str(save_path))
        
    # # 2. split
    # for file_path in file_paths:
    #     loader = PyPDFLoader(file_path)
    #     documents = loader.load()
        
    #     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    #     chunks = splitter.split_documents(documents)
        
    #     texts = [chunk.page_content for chunk in chunks]
    #     metadata = [chunk.metadata | {"text": chunk.page_content} for chunk in chunks]
    #     ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]
        
    #     # 3. Embedding
    #     print("Embedding chunks...")
    #     embeddings = embed_model.embed_documents(texts)
    #     print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

    #     # 4. Upsert
    #     print("Upserting embeddings...")
    #     with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
    #         index.upsert(vectors=zip(ids, embeddings, metadata))
    #         progress.update(len(embeddings))
            
    #     print(f"✅ Upload complete for {file_path}")
    # for file in uploaded_files:
    #     # Save to a temp file in /tmp
    #     with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp:
    #         temp.write(file.file.read())
    #         temp.flush()
    #         loader = PyPDFLoader(temp.name)
    #         documents = loader.load()

    #         splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    #         chunks = splitter.split_documents(documents)

    #         texts = [chunk.page_content for chunk in chunks]
    #         metadata = [chunk.metadata for chunk in chunks]
    #         ids = [f"{file.filename}-{i}" for i in range(len(chunks))]

    #         print("Embedding chunks...")
    #         embeddings = embed_model.embed_documents(texts)
    #         print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

    #         print("Upserting embeddings...")
    #         with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
    #             index.upsert(vectors=zip(ids, embeddings, metadata))
    #             progress.update(len(embeddings))
    #         print(f"✅ Upload complete for {file.filename}")
