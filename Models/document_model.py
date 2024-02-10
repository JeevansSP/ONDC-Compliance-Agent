from pydantic import BaseModel
from fastapi import UploadFile, Form

class DocumentUpload(BaseModel):
    user_id: str = Form(...)
    document_name: str = Form(...)
    document_category: str = Form(...)
    document_source_url: str = Form(...)
    upload_remark: str = Form(...)
    file: UploadFile = Form(...)


class VerifyDocument(BaseModel):
    verify_by: str = Form(...)
    document_id: str = Form(...)
    verify_remark:str = Form(...)
    is_legit: bool = Form(...)
    
    