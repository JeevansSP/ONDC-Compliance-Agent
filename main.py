from fastapi import (
    FastAPI,
    UploadFile,
    WebSocket,
    Form,
    File,
    Response,
    Request,
    Depends,
)
from fastapi.responses import RedirectResponse
from jose import jwt
from fastapi.middleware.cors import CORSMiddleware
from Auth import credential_handler
from DocumentHandler import *
from LLM import getDocumentGPT
from threading import Thread 
import uvicorn
from typing import Dict, List
import os
from Auth import *
from Models import *
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def welcome():
    return "Head to /docs"


@app.get("/login/google")
async def login_google():
    return loginUrl()


@app.get("/user/info")
async def get_token(access_token: str = Depends(oauth2_scheme)):
    if verify_access_token(access_token):
        return get_user_info(access_token)
    return {"message": "false"}

@app.post("/user/points")
async def update_points(access_token: str = Depends(oauth2_scheme), event: str = Form(...)):
    if verify_access_token(access_token):
        if event == "UPLOAD":
            return update_user_points(access_token, points=10)
        elif event == "VERIFY":
            return update_user_points(access_token, points=1)
        else:
            return {"message":"Specify it's UPLOAD or VERIFY event."}
    return {"message": "false"}

@app.post('/user/ranking')
async def get_ranking(access_token: str = Depends(oauth2_scheme)):
    if verify_access_token(access_token):
        return get_user_ranking()
    return {"message": "false"}

@app.get("/callback")
async def auth_google(request: Request):

    token = google_auth(str(request.query_params.get("code")))

    redirect_url = f"{hostingLink}/auth?token=" + token

    # Return a RedirectResponse with the desired URL
    return RedirectResponse(url=redirect_url)


@app.post("/insert/document")
async def uploadDocument(files: List[UploadFile]):
    """Uplaods and parses document"""
    for file in files:
        document_name = file.filename
        document_bytes = await file.read()
        try:
            insertDocument(document_name, document_bytes)
        except Exception as excep:
            print(excep)
        # Thread(
        #     target=insertDocument,
        #     args=(document_name, document_bytes),
        #     daemon=True,
        # ).start()

    return {"data": "Document parsing successful"}


@app.get("/fetch/document_list")
async def fetchDocumentList() -> Dict:
    """Fetches all documents in the db"""
    return {"data": listDocuments()}


@app.delete("/delete/document")
async def deleteDocument(document_id: int):
    removeDocument(document_id)
    return {"data": f"Document with id {document_id} deleted successfully"}


@app.post("/upload/pdfdoc")
async def uploadPdfDocument(
    request: Request,
    user_id: str = Form(...),
    document_name: str = Form(...),
    document_category: str = Form(...),
    document_source_url: str = Form(...),
    upload_remark: str = Form(...),
    file: UploadFile = File(...),
    access_token: str = Depends(oauth2_scheme),
    
):
    """Uploads docuements to be verified

    Parameters
    user_id : <string>
    document_name : <string>
    document_category : <string>
    document_source_url : <string>
    upload_remark : <string>
    file : UploadFile

    returns:
    Success Message

    # """

   
    details = DocumentUpload(
        user_id=user_id,
        document_name=document_name,
        document_category=document_category,
        document_source_url=document_source_url,
        upload_remark=upload_remark,
        file=file,
    )

    if verify_access_token(access_token):
        return await uploadUnverifiedDocuments(details)
    return {"error": "Unauthorized access"}


@app.get("/fetch/verifed/documents")
async def fetchVerifiedDocuments(
    access_token: str = Depends(oauth2_scheme),
) -> List[dict]:
    """Fetches all verified documents in the db"""
    if verify_access_token(access_token):
        return fetch_verified_documents()
    return {"error": "Unauthorized access"}


@app.get("/fetch/unverifed/documents")
async def unverifedDocuments(access_token: str = Depends(oauth2_scheme)) -> List[dict]:
    """Fetches all unverified documents in the db"""
    if verify_access_token(access_token):
        return fetch_unverified_documents()
    return {"error": "Unauthorized access"}


@app.post("/verify/document")
async def verifyDocument(
    docs: VerifyDocument
    , access_token: str = Depends(oauth2_scheme)
):
    """Once the document is verified. The legit document will be uploaded to the GPT and the user
    who uploaded will receive the reward."""

    if verify_access_token(access_token):
        return verify_document(docs=docs)

    return {"error": "Unauthorized access"}


# Path to the directory containing the PDF files


@app.get("/pdf")
async def get_pdf(filepath: str):
    # Gives the PDF file
    return get_pdf_document(filepath)


@app.websocket("/gpt")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    gpt = getDocumentGPT()

    await websocket.send_text("Hello I am your ONDC legal compliance assistant. You can ask me any product compliance related queries. How may I help you today?")

    try:
        while True:
            query = await websocket.receive_json()
            question = query.pop("question")

            response = gpt.run(
                f"""
                user question: {question}
                
                assume the below seed values for context around the above question unless explicitly mentioned in the above question:
                {str(query)}
                """
            )
            await websocket.send_text(response)
    except Exception as excep:
        print(f"Websocket [{websocket.client}]  disconnected due to {excep}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        log_config="./log.ini",
    )
