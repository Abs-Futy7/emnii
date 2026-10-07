# ResolveOps Backend

FastAPI backend for the ResolveOps multi-tenant customer support operations
platform. It currently includes authentication, organization-scoped client
management, structured dataset processing, document ingestion, and local
document-vector indexing.

## Local setup

Run these commands from `backend/` in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env` to a PostgreSQL SQLAlchemy URL, for example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:your-password@localhost:5432/resolveops
```

The local fallback URL is
`postgresql+psycopg://postgres:postgres@localhost:5432/resolveops`. Do not use
development credentials in staging or production.

## Database migrations

Once PostgreSQL is running and `DATABASE_URL` is configured:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The initial migration creates users, organizations, organization memberships,
client workspaces, and audit logs. Models exported from `app/db/models/` are
discovered through `app/db/base.py` and `alembic/env.py`.

The ownership hierarchy is:

```text
User <-> OrganizationMembership <-> Organization -> Client
                                         |----------> AuditLog
```

An organization is the ResolveOps tenant that owns users, permissions, and
billing boundaries. A client is a customer workspace managed by that tenant.
Keeping them separate lets one ResolveOps organization safely manage many client
workspaces without treating customer data as platform-user membership data.

## Run the API

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`, interactive documentation at
`http://localhost:8000/docs`, and health at
`http://localhost:8000/api/v1/health`.

Authentication uses JSON requests and bearer access tokens:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Set a random `JWT_SECRET` containing at least 32 characters before using these
routes. Client management is available under `/api/v1/clients`; every operation
is scoped to the organization in the authenticated token and revalidated against
the current database membership.

Client endpoints are:

- `POST /api/v1/clients`
- `GET /api/v1/clients`
- `GET /api/v1/clients/{client_id}`
- `PATCH /api/v1/clients/{client_id}`
- `DELETE /api/v1/clients/{client_id}` (soft-disables the client)

Structured datasets can be uploaded as multipart CSV, JSON, or XLSX files at
`POST /api/v1/clients/{client_id}/datasets`. Files are streamed to `UPLOAD_DIR`
(default `./storage/uploads`, ignored by Git) using generated internal names.
`MAX_UPLOAD_SIZE_MB` and `DATASET_MAX_ROWS` bound parsing resource usage. In a
deployed environment, apply a matching request-size limit at the reverse proxy
as well, since multipart decoding begins before application-level validation.

Dataset history and metadata are available at:

- `GET /api/v1/clients/{client_id}/datasets`
- `GET /api/v1/clients/{client_id}/datasets/{dataset_id}`

Schema mapping is deterministic and does not call an LLM:

- `POST /api/v1/clients/{client_id}/datasets/{dataset_id}/schema/detect`
- `GET /api/v1/clients/{client_id}/datasets/{dataset_id}/schema`
- `PUT /api/v1/clients/{client_id}/datasets/{dataset_id}/schema`

Detection normalizes names, checks canonical names and aliases, applies
RapidFuzz similarity, and optionally adds evidence from sampled email, phone,
or date values. Scores are explainable heuristic evidence values rather than
machine-learning probabilities. Scores below `0.72` remain unresolved.

Data quality reports are available at:

- `POST /api/v1/clients/{client_id}/datasets/{dataset_id}/validate`
- `GET /api/v1/clients/{client_id}/datasets/{dataset_id}/validation/latest`

The overall score is deterministic:

```text
score = 0.30 * completeness
      + 0.30 * validity
      + 0.25 * uniqueness
      + 0.15 * consistency
```

Issue rows contain at most five representative examples; complete invalid
datasets are never copied into the database.

PII scanning runs locally and never sends dataset values to an external API:

- `POST /api/v1/clients/{client_id}/datasets/{dataset_id}/pii/scan`
- `GET /api/v1/clients/{client_id}/datasets/{dataset_id}/pii`

Email, phone, IP address, and payment-card-like values use deterministic
patterns; card candidates must also pass the Luhn checksum. Person names and
addresses use approved or suggested canonical schema mappings. Findings store
only masked samples, never the original detected values.

## Knowledge-base documents

Authenticated users can upload PDF, DOCX, UTF-8 TXT, and Markdown documents:

- `POST /api/v1/clients/{client_id}/documents`
- `GET /api/v1/clients/{client_id}/documents`
- `GET /api/v1/clients/{client_id}/documents/{document_id}`
- `DELETE /api/v1/clients/{client_id}/documents/{document_id}`

Uploads are streamed to `DOCUMENT_UPLOAD_DIR` using generated filenames and are
limited by `MAX_DOCUMENT_UPLOAD_SIZE_MB`. Text extraction happens outside a
long-lived database transaction. The resulting text is split into overlapping
chunks controlled by `DOCUMENT_CHUNK_SIZE` and `DOCUMENT_CHUNK_OVERLAP`, then
stored in PostgreSQL with source and page metadata. Deletion is a recoverable
soft delete; any derived vectors are removed first.

`pypdf` can extract embedded text but cannot read pixels from image-only scanned
PDFs. Those documents fail with an OCR-specific message for now. A later OCR
stage could render pages and use an engine such as Tesseract before chunking.

## Local embedding index

Processed documents can be indexed explicitly:

- `POST /api/v1/clients/{client_id}/documents/{document_id}/index`
- `GET /api/v1/rag/health`
- `POST /api/v1/clients/{client_id}/search`

`EMBEDDING_MODEL` selects the local Sentence Transformers model, and
`EMBEDDING_BATCH_SIZE` controls batched encoding. The default is
`sentence-transformers/all-MiniLM-L6-v2`. The first use may need to download
model weights; after they are cached, inference is local and document text is
not sent to an embedding API.

If `CHROMA_HOST` is empty, Chroma uses a persistent local directory at
`CHROMA_PERSIST_DIR`. Setting `CHROMA_HOST`, `CHROMA_PORT`, and optionally
`CHROMA_SSL` selects a self-hosted Chroma server. Re-indexing computes the new
embeddings, removes the old document vectors, and upserts deterministic chunk
IDs so vectors are not duplicated.

PostgreSQL remains the source of truth for documents and chunks. Chroma is a
derived semantic-search index that can be rebuilt. Every vector operation uses
`organization_id` and `client_id` metadata filters during the operation itself;
tenant filtering is never deferred until after retrieval.

Semantic search embeds the query locally and asks Chroma for the nearest
tenant-scoped chunks. `RETRIEVAL_DEFAULT_TOP_K` sets the default result count,
while `RETRIEVAL_MAX_TOP_K` caps caller requests. An optional request-level
`score_threshold` can remove weak matches. The returned `score` is labeled
`normalized_cosine_similarity`: it maps Chroma cosine distance onto a bounded
0–1 ranking scale and is not a probability or confidence estimate.

## Run checks

```powershell
pytest
ruff check .
python -m compileall app tests
```

## Structure

- `app/api/` defines routing and HTTP dependencies.
- `app/core/` owns configuration, logging, and shared exceptions.
- `app/db/` owns SQLAlchemy metadata, sessions, and relational models.
- `app/schemas/` contains Pydantic transport models.
- `app/repositories/` isolates tenant-scoped database access.
- `app/services/` contains application orchestration outside route handlers.
- `app/services/documents/` contains storage, extraction, and chunking adapters.
- `app/services/rag/` contains swappable embedding, vector-store, and indexing
  adapters without implementing retrieval-augmented generation yet.
- `app/domain/` is reserved for framework-independent business concepts.
- `app/utils/` contains small cross-cutting helpers.
- `tests/` contains pytest fixtures and automated tests.
- `alembic/` contains database migration configuration and revisions.

