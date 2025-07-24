from fastapi import FastAPI
#from app.api.routes import upload, compare
from app.api.routes import upload,formrecognizer
app = FastAPI(
    title="Document Comparison API",
    description="API for uploading and comparing documents",
    version="1.0.0"
)

# Include routes
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(formrecognizer.router, prefix="/api/formrecognizer", tags=["formrecognizer"])