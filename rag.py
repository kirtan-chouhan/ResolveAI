import os
import time

from click import prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors
from pinecone import Pinecone

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing")

if not pinecone_api_key:
    raise ValueError("PINECONE_API_KEY is missing")


# ============================================================
# 2. Create API clients
# ============================================================

gemini = genai.Client(
    api_key=gemini_api_key
)

pc = Pinecone(
    api_key=pinecone_api_key
)

index = pc.Index("rag-v1")


# ============================================================
# 3. Configuration
# ============================================================

EMBEDDING_MODEL = "gemini-embedding-2"

EMBEDDING_DIMENSION = 768

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

# Keep total text in one embedding request reasonably below
# Gemini's shared input limit.
MAX_BATCH_CHARACTERS = 18000

# Pinecone can receive vectors in batches.
PINECONE_BATCH_SIZE = 100


# ============================================================
# 4. Generate embeddings for a batch of chunks
# ============================================================

def generate_embeddings(texts):

    if not texts:
        return []

    contents = []

    for text in texts:

        contents.append(
            types.Content(
                parts=[
                    types.Part.from_text(
                        text=text
                    )
                ]
            )
        )

    for attempt in range(3):

        try:

            result = gemini.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=contents,
                config=types.EmbedContentConfig(
                    output_dimensionality=EMBEDDING_DIMENSION
                )
            )

            if not result.embeddings:

                raise RuntimeError(
                    "Gemini returned no embeddings."
                )

            embeddings = [
                embedding.values
                for embedding in result.embeddings
            ]

            if len(embeddings) != len(texts):

                raise RuntimeError(
                    "Gemini returned a different number of "
                    "embeddings than input chunks."
                )

            return embeddings

        except errors.ClientError as e:

            # Retry temporary rate-limit errors.
            #
            # Important:
            # If this is a DAILY quota exhaustion,
            # retrying will not restore the quota.

            if getattr(e, "code", None) == 429:

                if attempt == 2:
                    raise

                wait_time = 5 * (attempt + 1)

                print(
                    f"Gemini rate limit reached. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise

    raise RuntimeError(
        "Embedding generation failed."
    )


# ============================================================
# 5. Build an embedding batch based on character size
# ============================================================

def create_embedding_batch(chunks):

    batch = []

    current_characters = 0

    for chunk in chunks:

        chunk_length = len(chunk["text"])

        # If adding this chunk would make the batch too large,
        # return the current batch first.

        if (
            batch
            and
            current_characters + chunk_length
            > MAX_BATCH_CHARACTERS
        ):
            break

        batch.append(chunk)

        current_characters += chunk_length

    return batch


# ============================================================
# 6. Upload vectors to Pinecone
# ============================================================

def upload_vectors(vectors, document_name):

    if not vectors:
        return

    for start in range(
        0,
        len(vectors),
        PINECONE_BATCH_SIZE
    ):

        batch = vectors[
            start:start + PINECONE_BATCH_SIZE
        ]

        index.upsert(
            vectors=batch,
            namespace=document_name
        )

        print(
            f"Pinecone: uploaded "
            f"{len(batch)} vectors"
        )


# ============================================================
# 7. Process an embedding batch
# ============================================================

def process_embedding_batch(
    chunks,
    document_name
):

    if not chunks:
        return 0

    print(
        f"\nEmbedding {len(chunks)} chunks..."
    )

    texts = [
        item["text"]
        for item in chunks
    ]

    embeddings = generate_embeddings(
        texts
    )

    vectors = []

    for item, embedding in zip(
        chunks,
        embeddings
    ):

        vector_id = (
            f"{document_name}-"
            f"page-{item['page_number']}-"
            f"chunk-{item['chunk_number']}"
        )

        vectors.append({

            "id": vector_id,

            "values": embedding,

            "metadata": {

                "text": item["text"],

                "document_name": document_name,

                "page_number": item["page_number"],

                "chunk_id": item["chunk_number"]

            }

        })

    upload_vectors(
        vectors,
        document_name
    )

    return len(vectors)


# ============================================================
# 8. Index a PDF document
# ============================================================

def index_document(
    pdf_path,
    document_name
):

    reader = PdfReader(
        pdf_path
    )

    text_splitter = RecursiveCharacterTextSplitter(

        chunk_size=CHUNK_SIZE,

        chunk_overlap=CHUNK_OVERLAP

    )

    total_pages = len(
        reader.pages
    )

    total_chunks = 0

    pending_chunks = []

    print(
        f"\nIndexing: {document_name}"
    )

    print(
        f"Total pages: {total_pages}"
    )


    # --------------------------------------------------------
    # Read PDF page by page
    # --------------------------------------------------------

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if not text:
            continue

        chunks = text_splitter.split_text(
            text
        )

        for chunk_number, chunk in enumerate(
            chunks
        ):

            pending_chunks.append({

                "text": chunk,

                "page_number": page_number,

                "chunk_number": chunk_number

            })


            # ------------------------------------------------
            # Process whenever the batch becomes large enough
            # ------------------------------------------------

            batch = create_embedding_batch(
                pending_chunks
            )

            if batch:

                batch_characters = sum(
                    len(item["text"])
                    for item in batch
                )

                # Process only when the batch has reached
                # the target size or there are enough chunks.

                if (
                    batch_characters
                    >= MAX_BATCH_CHARACTERS * 0.7
                ):

                    processed = process_embedding_batch(
                        batch,
                        document_name
                    )

                    total_chunks += processed

                    pending_chunks = pending_chunks[
                        len(batch):
                    ]


        print(
            f"Processed page "
            f"{page_number}/{total_pages}"
        )


    # ========================================================
    # Process remaining chunks
    # ========================================================

    while pending_chunks:

        batch = create_embedding_batch(
            pending_chunks
        )

        if not batch:
            break

        processed = process_embedding_batch(
            batch,
            document_name
        )

        total_chunks += processed

        pending_chunks = pending_chunks[
            len(batch):
        ]


    # ========================================================
    # Finished
    # ========================================================

    print(
        "\nDocument indexed successfully!"
    )

    print(
        f"Total chunks indexed: {total_chunks}"
    )

    return total_chunks


# ============================================================
# 9. Ask a question
# ============================================================

def ask_question(
    question,
    document_name
):
    start = time.time()
    # --------------------------------------------------------
    # Create question embedding
    # --------------------------------------------------------

    result = gemini.models.embed_content(

        model=EMBEDDING_MODEL,

        contents=question,

        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        )

    )

    question_vector = (
        result.embeddings[0].values
    )
    print("Question embedding time:", round(time.time() - start, 2), "seconds")

    # --------------------------------------------------------
    # Retrieve relevant chunks
    # --------------------------------------------------------

    search_result = index.query(

        vector=question_vector,

        top_k=3,

        include_metadata=True,

        namespace=document_name

    )
    print("Pinecone retrieval time:", round(time.time() - start, 2), "seconds")


    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    for match in search_result.matches:

        metadata = match.metadata or {}

        text = metadata.get(
            "text",
            ""
        )

        if text:

            context_parts.append(
                text
            )


    context = "\n\n---\n\n".join(
        context_parts
    )


    # --------------------------------------------------------
    # Create RAG prompt
    # --------------------------------------------------------

    prompt = f"""
You are a helpful assistant.

Answer the user's question using only
the context provided below.

If the answer cannot be found in the context,
say exactly:

"I don't know based on the provided documents."

CONTEXT:
{context}

QUESTION:
{question}
"""

    
    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    generation_start = time.time()

    response = gemini.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal"
            )
        )
    )

    print(
        "Gemini generation time:",
        round(time.time() - generation_start, 2),
        "seconds"
    )

# --------------------------------------------------------
# Return answer
# --------------------------------------------------------

    return response.text