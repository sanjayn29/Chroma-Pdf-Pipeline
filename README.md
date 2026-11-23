# Chroma PDF Pipeline

This project is a small PDF-to-vector-database pipeline. It extracts text from
a PDF, stores it with ChromaDB's automatically generated embeddings, and can
print the stored records for inspection. The current implementation uses each
non-empty PDF page as one record; it does **not** yet split page text into
smaller, fixed-size text chunks.

## Project files

- `app.py` — command-line program for ingesting a PDF and displaying the
  collection.
- `book.pdf` — example input PDF.
- `my_chroma_db/` — ChromaDB's persistent local database files. This directory
  is created and managed by ChromaDB; do not edit its internal files manually.

The project `.gitignore` excludes PDFs and the generated `my_chroma_db/`
directory so source documents and local database files are not uploaded to Git.
Keep the PDF in the project folder locally, or pass its full path when running
the script. If you intentionally want to track a PDF, remove the `*.pdf` rule
or add a specific exception to `.gitignore`.

## How the pipeline works

1. **Select the database.** The script sets `db_path` to `my_chroma_db` beside
   `app.py`, regardless of the folder from which the command is run.
2. **Open the collection.** It opens or creates a collection named
   `pdf_documents`.
3. **Read the PDF.** When a PDF path is provided, `pypdf.PdfReader` reads the
   document and `extract_text()` extracts text page by page. Empty pages are
   skipped. This extracts embedded text; it does not perform OCR on scanned
   page images.
4. **Create page records.** Each non-empty page is stored as a document, with
   metadata containing its one-based `page_number` and an ID such as
   `page_1`.
5. **Create embeddings and persist records.** ChromaDB's default embedding
   function converts each document into a vector and saves the document,
   metadata, ID, and vector in the local collection.
6. **Display the collection.** The script prints the database path, collection
   name, total record count, and each record's ID, metadata, text preview, and
   first five embedding values.

## Pages and chunks

In this project, a **record** is currently one non-empty PDF page. This makes
the page number easy to trace back to the source, but a page is not the same as
a text chunk:

- A **page record** may contain a short page or a very long page.
- A **text chunk** is a smaller, bounded piece of text, often split by
  character or token count, optionally with overlap between neighboring
  pieces.
- This code does not have a chunk size, overlap, or chunking step. It sends
  each full extracted page to ChromaDB as one document.

For a future question-answering or semantic-search feature, splitting long
pages into smaller chunks can make retrieved passages more focused. Each chunk
should retain its source page number and have its own stable ID, for example
`page_12_chunk_3`. Chunking would change the stored record format and require
re-ingesting the PDF to populate chunks; it is not performed by the current
script.

## Where paths and settings are specified

- **Input PDF path:** supplied as the optional command-line argument. It is not
  hard-coded in `app.py`.
- **Database path:** the `db_path` expression in `app.py` points to the
  `my_chroma_db` directory beside the script.
- **Collection name:** `pdf_documents` in `app.py`.
- **Page record ID:** generated in `app.py` from the page number, such as
  `page_12`.
- **Page metadata:** currently contains `page_number`.

## Requirements

Install the Python dependencies from PowerShell:

```powershell
python -m pip install chromadb pypdf
```

## Run

From the project folder, ingest `book.pdf` and then display the collection:

```powershell
python app.py "C:\Users\sanja\OneDrive\Desktop\Documents\Projects\Chroma Pdf Pipeline\book.pdf"
```

You can also use a relative path when the terminal is in the project folder:

```powershell
python app.py book.pdf
```

To display the existing collection without ingesting a PDF:

```powershell
python app.py
```

## Re-ingesting PDFs

The script uses `collection.upsert()`. If a record ID already exists, that
record is updated; otherwise it is inserted. Since IDs are based only on page
number, ingesting another PDF into the same collection can replace records
with matching page IDs. Records from a previous, longer PDF whose page IDs
were not overwritten can remain in the collection. Use a separate collection
per source PDF or clear the collection deliberately when you need strict
separation; this script does not currently do that automatically.

## What the display means

- **Records** is the total number of stored page records, not necessarily the
  number of pages in the most recently ingested PDF.
- **Text preview** shows up to the first 150 characters of the extracted page
  text.
- **Embedding (first 5 dimensions)** is only a short sample of the numeric
  vector. The full vector is stored in ChromaDB and is not printed in the
  output.

Displaying records is for inspection. The program does not currently provide a
query interface, similarity search, answer generation, OCR, or automatic
fixed-size chunking.

# 👨‍💻 Developer

**Sanjay N**

🚀 Freelancer  

🌐 Portfolio: https://sanjayn.me  
💼 LinkedIn: https://linkedin.com/in/sanjayn29  
🐙 GitHub: https://github.com/sanjayn29  

---

# ⭐ Support

If you like this project, consider giving it a **star ⭐ on GitHub** to support the development.
