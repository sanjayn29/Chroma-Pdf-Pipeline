# ChromaDB: Structure, Local vs. Cloud, and Interview Guide

This guide explains the concepts behind ChromaDB and relates them to this
project's PDF pipeline. It is intended as a learning and interview-preparation
document; the code snippets are illustrative and may need adjustment for the
ChromaDB version and deployment you use.

## 1. What is ChromaDB?

ChromaDB (often called Chroma) is a database designed to store and retrieve
data using vector embeddings. It is commonly used in semantic search and
retrieval-augmented generation (RAG) applications.

An application can store text along with an embedding, an ID, and metadata.
When a user submits a query, the query is embedded into a vector and Chroma
finds records whose vectors are close to it according to a distance metric.
The application can then use the retrieved text as context for another step,
such as answering a question with a language model.

ChromaDB is not itself a language model and does not automatically answer
questions. It stores and retrieves records; an application supplies any
additional retrieval, prompt construction, and answer-generation behavior.

## 2. The main data hierarchy

The conceptual structure is:

```text
Client
└── Database
    └── Collection
        └── Record (also commonly called an item)
            ├── ID
            ├── Document (optional text or other text content)
            ├── Metadata (optional key/value attributes)
            └── Embedding (a numeric vector)
```

### Client

A client is the application's connection to ChromaDB. The client determines
how the database is reached: an embedded local persistent database, a
separately hosted Chroma server, or Chroma Cloud.

### Database and tenant

In a hosted or multi-tenant deployment, a tenant and database provide
organizational and isolation boundaries. The exact setup depends on the
deployment. A simple local `PersistentClient` project may not need the
application to select these explicitly.

### Collection

A collection groups related records. It is where an application adds, reads,
updates, deletes, and queries records. A collection can also be configured
with an embedding function and distance behavior. For example, an application
might use separate collections for different datasets or use cases.

### Record

A record is one stored item in a collection:

- **ID:** Unique within its collection. The application supplies it.
- **Document:** Optional human-readable content, commonly a text passage.
- **Metadata:** Optional structured attributes, such as source file, page
  number, category, or date. Metadata is useful for filtering and attribution.
- **Embedding:** A list of numbers representing the content in vector space.
  Chroma can generate it from a document using an embedding function, or the
  application can supply it.

Records need IDs. If an ID is already present, `add()` and `upsert()` have
different semantics: `add()` is for adding new IDs, while `upsert()` inserts
missing IDs and updates existing IDs. Use stable IDs that represent the
intended record identity.

## 3. How vector search works

1. **Prepare content.** Extract text and, when appropriate, split it into
   useful passages or chunks.
2. **Embed content.** An embedding model maps each passage to a numeric vector.
3. **Store records.** Store vectors with their IDs and optionally their source
   documents and metadata.
4. **Embed a query.** Convert a user's search text into a vector using a
   compatible embedding model.
5. **Retrieve neighbors.** The database finds records with vectors near the
   query vector and returns the best matches, optionally with metadata filters.
6. **Use the results.** The application presents the results or supplies them
   as context to another component, such as an LLM.

Vector similarity is not keyword search. It compares vector representations
according to a configured distance space, such as squared L2, cosine, or inner
product. The chosen metric and embedding model affect retrieval results.

An approximate nearest-neighbor index can make vector search efficient at
scale. Index implementation and storage details are internal and may change
between ChromaDB versions and deployment modes; applications should use the
ChromaDB API rather than editing internal database files.

## 4. Local, self-hosted, and cloud deployments

ChromaDB can be used in different deployment modes. These are ways of running
or connecting to ChromaDB, not different meanings of a collection or record.

| Mode | Where data lives | Typical connection | Operations to consider |
| --- | --- | --- | --- |
| Local persistent | On the machine running the application | Python `PersistentClient` | Local disk space, backups, machine access, and local lifecycle |
| Self-hosted server | On infrastructure managed by the project or organization | HTTP client to a Chroma server | Server operations, network security, persistence, backups, scaling |
| Chroma Cloud | In Chroma's managed cloud service | Cloud client and configured credentials | Cloud account, authentication, tenant/database selection, network access, and service plan |

### Is this project using cloud?

**No. The current project uses local persistent storage.** In `app.py`, it
creates a `chromadb.PersistentClient` pointed at the `my_chroma_db` directory
beside the script. The database is stored on that machine. The code does not
configure a cloud client, a remote server URL, or cloud credentials.

The PDF is also read locally from the path passed to the program. The
`.gitignore` excludes PDFs and the generated database directory so they are
not included in normal Git commits. That is a source-control rule, not a
database access-control or encryption feature.

To move from local storage to a hosted service, an application must deliberately
configure and use the appropriate hosted client, credentials, target database,
and network settings. Copying or uploading the local database folder is not a
substitute for configuring a cloud connection. Follow the current ChromaDB
documentation for the selected service and version.

### Local persistent storage does not mean "no persistence"

`PersistentClient` saves data locally so it can be reopened by a later run of
the application. It is persistent across program runs, but it is not
automatically replicated or backed up to the cloud. Losing or deleting the
local database files can lose the stored data. Treat the database as
application-managed data and plan backups if it matters.

### Does Chroma send data to the cloud?

This project's configured database client is local, so its records are stored
in the configured local persistence directory. However, the code uses
ChromaDB's default embedding behavior, which may download a model the first
time it is needed and then use the installed model locally. Review the
embedding function, package behavior, and any telemetry/configuration for the
exact version and environment before making privacy or compliance claims.
Changing to a hosted Chroma service means records are sent to that service.

## 5. How this project maps to ChromaDB

The current pipeline works as follows:

1. The optional command-line argument supplies the input PDF path.
2. `pypdf` extracts text from each page with extractable text.
3. Each non-empty **page** is currently one Chroma document/record. The
   program does not split a page into smaller fixed-size text chunks.
4. The record ID is currently `page_1`, `page_2`, and so on.
5. Metadata currently contains `page_number`.
6. ChromaDB generates embeddings using the collection's default embedding
   function when documents are upserted.
7. The records are stored in the local `pdf_documents` collection under
   `my_chroma_db`.
8. The script retrieves and prints the IDs, metadata, a short text preview,
   and the first five embedding values.

For this project, "chunk" is often used informally to mean a stored passage,
but technically the current stored passage is a whole extracted page. A
production RAG pipeline often splits long pages into smaller chunks and stores
source information such as the PDF filename and page number in metadata.

### Important current ID behavior

The current ID is based only on page number. If a second PDF is ingested into
the same collection, `upsert()` can overwrite records with matching page IDs.
If the new PDF has fewer pages, older records from higher page numbers can
remain. A safer multi-PDF design uses IDs that include source identity, such
as a stable hash or document key plus page/chunk number, and stores the source
filename in metadata.

## 6. Interview questions and answers

### Fundamentals

**1. What is ChromaDB?**  
ChromaDB is a vector database used to store embeddings and retrieve records by
vector similarity, often for semantic search and RAG.

**2. What is an embedding?**  
An embedding is a numeric vector produced from content by an embedding model.
The vector represents learned features of the content so related items can
often be found near one another in vector space.

**3. What is the difference between a document and an embedding?**  
A document is the original content, such as text. An embedding is the numeric
representation used for vector similarity search. A record can store both.

**4. What are IDs used for?**  
IDs identify records within a collection and allow them to be retrieved,
updated, or deleted. Applications should generate stable, unique IDs for the
records they intend to distinguish.

**5. What is metadata?**  
Metadata is structured information attached to a record, for example a source
filename, page number, date, or category. It supports filtering, attribution,
and application logic.

**6. What is a collection?**  
A collection is a named group of records that an application manages and
searches. It can represent a dataset, project, or retrieval use case.

**7. What is the difference between keyword search and vector search?**  
Keyword search matches terms or lexical structure. Vector search compares
embeddings and can find semantically related text even when it uses different
words. Many applications combine both approaches.

### Retrieval and RAG

**8. What is RAG?**  
Retrieval-augmented generation retrieves relevant context for a user query and
provides that context to a generative model. ChromaDB can be the retrieval
store; it does not itself provide the entire RAG application.

**9. Why split a document into chunks?**  
Very large documents may exceed model input limits or produce imprecise
retrieval. Smaller passages can make matches more focused. Chunk size and
overlap should be selected and evaluated for the content and use case.

**10. What is chunk overlap?**  
Overlap repeats some content between adjacent chunks. It helps preserve
context across a boundary but increases the amount of stored text and can
create redundant results.

**11. What metadata is useful for PDF retrieval?**  
Common fields include source filename or document ID, page number, chunk
number, title, and access-control attributes where applicable. Metadata makes
it possible to identify and filter retrieved passages.

**12. What is a metadata filter?**  
A metadata filter restricts which records can match a query, for example to a
particular source document or category. It narrows the retrieval scope; it does
not replace proper authorization checks in the application.

**13. How do you evaluate retrieval quality?**  
Create representative queries with expected relevant sources, then measure
whether relevant results appear near the top (for example, precision/recall at
K or ranking metrics). Also evaluate end-to-end answer quality, latency, and
cost for the application.

### Embeddings and similarity

**14. Why must query and document embeddings be compatible?**  
The query and stored vectors need to occupy a compatible vector space. Use the
same embedding model and compatible preprocessing for both sides; otherwise,
distance comparisons may be meaningless.

**15. What happens if the embedding model changes?**  
Vectors created by different models are generally not directly comparable.
Re-embed the stored documents with the new model and query with that model,
then validate retrieval quality. Keep model/version information with the
dataset when it is important for reproducibility.

**16. What do cosine distance, L2 distance, and inner product mean?**  
They are different ways of comparing vectors. Cosine focuses on vector
direction, L2 measures Euclidean distance, and inner product measures a
dot-product score. Their interpretation and whether larger or smaller scores
are better depend on the configured space and API response.

**17. Is the nearest result always relevant?**  
No. Vector search returns the nearest available vectors, even if all matches
are poor. Applications should consider thresholds, filters, reranking,
evaluation, and a graceful "no good match" behavior.

**18. Why might a relevant document not be retrieved?**  
Possible causes include poor extraction, unsuitable chunk boundaries,
inappropriate embedding model, incompatible query and document embeddings,
wrong distance configuration, restrictive filters, or a small result limit.

### Database operations and deployment

**19. What is the difference between `add`, `update`, and `upsert`?**  
Conceptually, `add` inserts new records, `update` modifies existing records,
and `upsert` inserts records that are missing while updating records whose IDs
already exist. Check the API version's exact validation and update behavior.

**20. What is the difference between `get` and `query`?**  
`get` retrieves records by IDs or filters without performing nearest-vector
search. `query` performs similarity search using a query vector or query text
when an embedding function is configured.

**21. Is this project using Chroma Cloud?**  
No. It constructs a local `PersistentClient` and uses a directory beside
`app.py`. There is no cloud endpoint or hosted-service credential configured.

**22. What is the difference between a local persistent client and a cloud
database?**  
A local persistent client stores data on local disk and is operated with the
application's environment. A cloud database is remotely hosted and requires
network access and service-specific connection/authentication settings. Cloud
hosting changes operational responsibilities and data location.

**23. Does a local ChromaDB automatically back up data?**  
No. Persistence saves data between runs, but it is not the same as a backup,
replication, or disaster-recovery plan. Backups should follow the database's
documented procedures and account for consistency and restore testing.

**24. Can ChromaDB store documents without embeddings?**  
Chroma's API supports storing records with different combinations of
documents, metadata, and embeddings depending on how records are supplied.
For similarity search, a usable embedding is required. Applications should
use the API's documented behavior for their version.

**25. Should the ChromaDB internal files be edited directly?**  
No. Use the ChromaDB client API. Internal files and formats are implementation
details and direct edits can corrupt data or break compatibility.

**26. Is ChromaDB a relational database?**  
It is optimized for vector-oriented retrieval and record management, not as a
general replacement for a relational database. Applications often keep
transactional business data in a relational database and use a vector database
for semantic retrieval.

**27. How should multiple PDFs be isolated in this project?**  
Use IDs that include stable source identity, include source metadata, and
decide whether to use one collection with filters or separate collections.
Avoid IDs based only on page number because different PDFs share page numbers.

**28. How would you handle scanned PDFs?**  
The current `pypdf` extraction step cannot read text that exists only as page
images. Add an OCR step, validate its output, and preserve page/source
metadata before creating records.

**29. How do you prevent unauthorized users from retrieving records?**  
Enforce authorization in the application and scope every retrieval to records
the user is allowed to access. Do not treat a metadata filter supplied by an
untrusted client as the only security boundary. Consider tenant isolation,
credential management, and deployment-specific access controls.

**30. What should be considered before moving this app to production?**  
Use robust IDs and source tracking, intentional chunking, ingestion error
handling, model/version tracking, retrieval evaluation, backups, access
controls, observability, resource limits, and a deliberate local/server/cloud
deployment plan. Avoid printing entire documents or vectors when they may
contain sensitive data.

## 7. Short interview summary

> ChromaDB is a vector database. In this project, `app.py` extracts text from
> PDF pages, stores each non-empty page as a record in the `pdf_documents`
> collection, and lets Chroma generate embeddings. The collection is persisted
> locally in `my_chroma_db` through `PersistentClient`; this project is not
> configured to use Chroma Cloud. The current pipeline stores whole pages, not
> smaller fixed-size chunks, and its page-only IDs need improvement before
> safely combining multiple PDFs.

## 8. Further reading

ChromaDB APIs and deployment options can evolve. For implementation details,
confirm behavior against the official documentation matching the installed
version:

- [Chroma documentation](https://docs.trychroma.com/)
- [Chroma cookbook](https://cookbook.chromadb.dev/)