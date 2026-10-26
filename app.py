import argparse
from pathlib import Path
import sys

import chromadb

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(errors="backslashreplace")


parser = argparse.ArgumentParser(
    description="Display the ChromaDB collection, or ingest a PDF before displaying it."
)
parser.add_argument(
    "pdf_path",
    type=Path,
    nargs="?",
    help="Optional path to a PDF file to ingest",
)
args = parser.parse_args()

db_path = Path(__file__).resolve().parent / "my_chroma_db"
client = chromadb.PersistentClient(path=str(db_path))

# Get the existing collection, creating it only if the database has not been
# initialized yet.
collection = client.get_or_create_collection(name="pdf_documents")

if args.pdf_path:
  if not args.pdf_path.is_file():
    parser.error(f"PDF file does not exist: {args.pdf_path}")

  from pypdf import PdfReader

  reader = PdfReader(args.pdf_path)
  documents = []
  metadatas = []
  ids = []

  for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text and text.strip():
      documents.append(text)
      metadatas.append({"page_number": i + 1})
      ids.append(f"page_{i + 1}")

  if not documents:
    parser.error(f"No extractable text found in PDF: {args.pdf_path}")

  collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
  print(f"Stored {len(documents)} pages from {args.pdf_path.name}.")

print(f"\nDatabase: {db_path}")
print(f"Collection: {collection.name}")
print(f"Records: {collection.count()}")

stored_data = collection.get(include=["documents", "metadatas", "embeddings"])
if not stored_data["ids"]:
  print("The collection is empty.")
else:
  print("\n--- Stored Records ---")
  for doc_id, text, metadata, embedding in zip(
      stored_data["ids"],
      stored_data["documents"],
      stored_data["metadatas"],
      stored_data["embeddings"],
  ):
    preview = " ".join((text or "").split())[:150]
    embedding_preview = embedding[:5].tolist()
    print(f"\nID: {doc_id}")
    print(f"Metadata: {metadata}")
    print(f"Text preview: {preview}{'...' if len(text or '') > 150 else ''}")
    print(f"Embedding (first 5 dimensions): {embedding_preview}")