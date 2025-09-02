# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from docling.document_converter import DocumentConverter
import tempfile
import shutil
import os
import uuid
from typing import Dict

app = FastAPI(title="Docling Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)


DOC_STORE: Dict[str, str] = {}



class StoreIn(BaseModel):
    markdown: str


class StoreOut(BaseModel):
    id: str


# =Endpoints ===
@app.post("/convert")
async def convert_document(file: UploadFile = File(...)):
      



    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        converter = DocumentConverter()
        result = converter.convert(temp_path)


        markdown = result.document.export_to_markdown()
        json_obj = result.document.model_dump()  

        return {"markdown": markdown, "json": json_obj}

    except Exception as e:
      
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@app.post("/store", response_model=StoreOut)
async def store_markdown(payload: StoreIn):
    


    try:
        doc_id = uuid.uuid4().hex  # id curtinho
        DOC_STORE[doc_id] = payload.markdown or ""
        return {"id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/doc/{doc_id}")
async def get_doc(doc_id: str):
    



    md = DOC_STORE.get(doc_id)
    if md is None:
        raise HTTPException(status_code=404, detail="doc not found")
    return {"markdown": md}


@app.get("/health")
async def health():
    return {"status": "ok"}
