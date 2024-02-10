from DatabaseHandler import *
from fastapi import File
from fastapi.responses import FileResponse
from Ocr import extractTextAndTables
from LLM import DocumentReformatChain
import json
from typing import List, Dict
import os
import datetime
from Models import *
from DocumentHandler.config import *
import shutil
from threading import Thread


def insertDocument(document_name: str, document_bytes: bytes):
    """Perform OCR on the pdf to extract all text/image contents,
    then picks out all necessarry labels from the document,
    finally breaks it into chunks for easier RAG and stores it all in the database.

    Args:
        document_name (str): name of the document.
        file_bytes (bytes): document content.
    """

    if executeQueryAndReturnJson(
        f"select 1 from {documents_table} where document_name='{document_name}'"
    ):
        raise FileExistsError(f"There exists a document with the name {document_name}")

    ocr_content = extractTextAndTables(document_bytes)
    if len(ocr_content.split(" ")) > 80_000:
        raise MemoryError("give file is too large to be parsed")
    reformatted_ocr = DocumentReformatChain().run({"ocr": ocr_content})
    reformatted_ocr = json.loads(
        reformatted_ocr[reformatted_ocr.find("{") : reformatted_ocr.rfind("}") + 1]
        .replace("\n", "")
        .replace("  ", "")
    )
    document_summary = reformatted_ocr["sections"]
    document_tags = reformatted_ocr["tags"]

    query = f"Insert into {documents_table} (document_name, document_summary, document_tags, document_raw) values(?,?,?,?)"
    values = (
        document_name,
        json.dumps(document_summary),
        json.dumps(document_tags),
        json.dumps(ocr_content),
    )
    executeNonSelectQuery(query, values)


def listDocuments() -> List[Dict]:
    """Retreives all the documents."""
    result = executeQueryAndReturnJson(
        f"select document_id, document_name, document_tags from {documents_table}"
    )
    for row in result:
        row["document_tags"] = json.loads(row["document_tags"])
    return result


def removeDocument(document_id: int):
    """deletes document from the db

    Args:
        document_id (int): id of the document to be deleted.
    """

    executeNonSelectQuery(
        f"delete from {documents_table} where document_id=?", (document_id,)
    )


async def uploadUnverifiedDocuments(details: DocumentUpload):
    """This functions will save the document to a folder call "UnverifiedDocuments" later to be verified"""

    current_date_time = datetime.datetime.now()

    if details.file.filename.endswith(".pdf"):
        file_path = os.path.join(
            unverified_documents_folder, details.document_name + ".pdf"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await details.file.read())
                query = f"""INSERT INTO {unverified_document_table} 
                (
                document_name,
                upload_date,
                document_category,
                document_source_url,
                document_url,
                upload_user_id,
                upload_remark
                ) 
                VALUES (?,?,?,?,?,?,?)"""
                values = (
                    details.document_name,
                    current_date_time,
                    details.document_category,
                    details.document_source_url,
                    os.path.dirname(file_path) + "/" + details.document_name + ".pdf",
                    details.user_id,
                    details.upload_remark,
                )
                executeNonSelectQuery(query, values)
                return {"message": "File successfully uploaded"}

        except Exception as excep:
            return {
                "error": f"Could not upload file {details.file.filename} due to {excep}"
            }
    else:
        return {"error": "Invalid file format. Only PDF files are allowed."}


def fetch_unverified_documents():
    result = executeQueryAndReturnJson(f"SELECT * FROM {unverified_document_table} WHERE document_verified = 0 LIMIT 1;")
    # for row in result:
    #     row["document_url"] = f"{hostingLink}{row['document_url']}"
    return result


def fetch_verified_documents():
    result = executeQueryAndReturnJson(f"SELECT * FROM {unverified_document_table} WHERE document_verified = 1;")
    # for row in result:
    #     row["document_url"] = f"{hostingLink}{row['document_url']}"
    return result


def verify_document(docs: VerifyDocument):
    #Getting the current directory
    current_path = os.getcwd()

    #Getting the unverified document 
    query_get_details = f"SELECT * FROM {unverified_document_table} WHERE document_id={docs.document_id} AND document_verified=0"
    unverified_document_details = executeQueryAndReturnJson(query_get_details)

    if unverified_document_details is []:
        return {"message": "No Document to verify."}
    
    #Getting the path of the unverified documents folder
    un_verified_documents_folder_path = os.path.join(
        current_path, unverified_documents_folder
    )

    #Getting the path of the verified documents folder
    verified_documents_folder_path = os.path.join(
        current_path, verified_documents_folder
    )
   
    #Getting the path of the Invalid documents folder
    invalid_documents_folder_path = os.path.join(current_path, invalid_documents_folder)

    update_db_query = f"""
        UPDATE {unverified_document_table} 
        SET 
        document_verified=?,
        verified_user_id=?,
        verify_remark=?,
        verify_date=?,
        document_url=?
        WHERE 
        document_id=?
        """
    
    update_user_points = f"""
        UPDATE {user_table} 
        SET 
        user_points=user_points+?
        WHERE
        user_id=?
    """

    if docs.is_legit:
        document_path = os.path.join(
            unverified_documents_folder,
            unverified_document_details[0]["document_name"] + ".pdf",
        )
        shutil.move(document_path, verified_documents_folder_path)
        current_date_time = datetime.datetime.now()
        values = (
            1,
            docs.verify_by,
            docs.verify_remark,
            current_date_time,
            verified_documents_folder
            + "/"
            + unverified_document_details[0]["document_name"]
            + ".pdf",
            docs.document_id,
        )
        executeNonSelectQuery(update_db_query, values)

        #Points for the verifier
        executeNonSelectQuery(update_user_points, (1,docs.verify_by))

        #Points for the Uploader
        executeNonSelectQuery(update_user_points, (10,unverified_document_details[0]['upload_user_id']))
        
        # The code block is opening a PDF file in binary mode using the `open()` function. It reads
        # the contents of the file and stores it in the `doc_bytes` variable.

        with open(verified_documents_folder_path
            + "/"
            + unverified_document_details[0]["document_name"]
            + ".pdf", 'rb') as f:
            doc_bytes = f.read()
        Thread(
            target=insertDocument,
            args=(unverified_document_details[0]["document_name"] + ".pdf", doc_bytes),
            daemon=True,
        ).start()

        return {"message": "Document verified"}
    else:
        document_path = os.path.join(
            un_verified_documents_folder_path,
            unverified_document_details[0]["document_name"] + ".pdf",
        )
        shutil.move(document_path, invalid_documents_folder_path)
        current_date_time = datetime.datetime.now()
        values = (
            -1,
            docs.verify_by,
            docs.verify_remark,
            current_date_time,
            invalid_documents_folder
            + "/"
            + unverified_document_details[0]["document_name"]
            + ".pdf",
            docs.document_id,
        )
        executeNonSelectQuery(update_db_query, values)

        #Points for the verifier and no points for the uploader because they have uploaded the invalid law.
        executeNonSelectQuery(update_user_points, (1,docs.verify_by))

        return {"message": "Document Marked Invalid"}

def get_pdf_document(filepath: str):
    
    # Check if the file exists
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    
    # Return the PDF file as a response
    return FileResponse(filepath, media_type="application/pdf")
