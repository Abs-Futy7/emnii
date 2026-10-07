from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.clients import router as clients_router
from app.api.v1.endpoints.datasets import router as datasets_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.pii import router as pii_router
from app.api.v1.endpoints.rag import router as rag_router
from app.api.v1.endpoints.schema_mapping import router as schema_mapping_router
from app.api.v1.endpoints.validation import router as validation_router

router = APIRouter()
router.include_router(auth_router, tags=["authentication"])
router.include_router(clients_router, tags=["clients"])
router.include_router(datasets_router, tags=["datasets"])
router.include_router(documents_router, tags=["documents"])
router.include_router(schema_mapping_router, tags=["schema-mapping"])
router.include_router(validation_router, tags=["validation"])
router.include_router(health_router, tags=["health"])
router.include_router(pii_router, tags=["pii"])
router.include_router(rag_router, tags=["rag"])
