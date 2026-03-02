"""
TinyCloudGallery main module - All files in src folder
"""

import boto3
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Company Document Manager")

s3_client = boto3.client("s3")
BUCKET_NAME = "company-document-manager"

# Helper function to read HTML files
def read_html_file(filename):
    with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Serve HTML pages
@app.get("/")
async def root():
    return read_html_file("index.html")

@app.get("/upload")
async def upload_page():
    return read_html_file("upload.html")

@app.get("/download")
async def download_page():
    return read_html_file("download.html")

# Serve CSS file
@app.get("/style.css")
async def get_css():
    with open(os.path.join(BASE_DIR, "style.css"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/css")

# API Endpoints
@app.get("/api/list")
def list_objects(role: Optional[str] = None, doc_type: Optional[str] = None):
    """List objects with optional filters"""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        objects = response.get("Contents", [])
        
        result = []
        for obj in objects:
            try:
                head = s3_client.head_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                metadata = head.get("Metadata", {})
                
                if role and metadata.get("role") != role:
                    continue
                if doc_type and metadata.get("doc_type") != doc_type:
                    continue
                    
                result.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "metadata": metadata
                })
            except:
                result.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "metadata": {}
                })
        
        return {"objects": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_name: str = Form(...),
    role: str = Form(...),
    doc_type: str = Form(...)
):
    """Upload document with metadata"""
    allowed = {".jpg", ".jpeg", ".png", ".pdf", ".txt"}
    
    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return {"error": f"File type not allowed: {ext}"}
    
    if role not in ["owner", "manager", "worker"]:
        return {"error": "Invalid role"}
    if doc_type not in ["contract", "report", "invoices"]:
        return {"error": "Invalid document type"}
    
    try:
        # Ensure filename has extension
        if not doc_name.endswith(ext):
            doc_name = doc_name + ext
            
        content = await file.read()
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=doc_name,
            Body=content,
            Metadata={
                "role": role,
                "doc_type": doc_type
            }
        )
        return {"message": "Upload successful", "filename": doc_name}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/download/{doc_name}")
def download_document(doc_name: str):
    """Download document"""
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=doc_name)
        return StreamingResponse(
            response["Body"].iter_chunks(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={doc_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

@app.get("/api/search")
def search_documents(q: str = "", role: str = "", doc_type: str = ""):
    """Search documents"""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        objects = response.get("Contents", [])
        
        results = []
        for obj in objects:
            # Filter by name
            if q and q.lower() not in obj["Key"].lower():
                continue
                
            try:
                head = s3_client.head_object(Bucket=BUCKET_NAME, Key=obj["Key"])
                metadata = head.get("Metadata", {})
                
                if role and metadata.get("role") != role:
                    continue
                if doc_type and metadata.get("doc_type") != doc_type:
                    continue
                    
                results.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "metadata": metadata
                })
            except:
                if not role and not doc_type:
                    results.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "metadata": {}
                    })
        
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)