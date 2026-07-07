from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ingest, query

app = FastAPI(
    title="Autonomous Product Intelligence & Decision Support System",
    description="Multi-agent RAG platform for product/customer/engineering intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(query.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "product-intelligence-platform"}


@app.get("/health")
def health():
    return {"status": "healthy"}
