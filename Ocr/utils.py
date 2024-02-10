"""utiliy methods for OCR functionality"""

import pdfplumber
from io import BytesIO
from typing import List, Dict, Union
import cv2
import numpy as np
import base64
from typing import List
import os
from LLM import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


import requests
from LLM import generateImageDescription


def rotateAndFlipImageBytes(image_bytes: bytes) -> bytes:
    """When image is extracted it is by default rotated and flipped.
    This method will get it back to normal.

    Args:
        image_bytes (bytes): bytes content of the image

    Returns:
        bytes
    """
    image_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Rotate the image 180 degrees clockwise
    rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    rotated_image = cv2.rotate(rotated_image, cv2.ROTATE_90_CLOCKWISE)

    # Flip the rotated image horizontally
    flipped_image = cv2.flip(rotated_image, 1)

    # Encode the flipped image back into bytes
    try:
        flipped_image_bytes = cv2.imencode(".jpg", flipped_image)[1].tobytes()
    except:
        flipped_image_bytes = None

    return flipped_image_bytes


def extractTextAndTables(pdf_content: bytes) -> str:
    """Extracts text and tables form pdf

    Args:
        pdf_content (bytes): bytes content of the pdf

    Returns:
        str: extract content where pages are separated by `--`
    """
    print("ocr started...")
    pages: List[Dict] = []
    cntr = 0
    with BytesIO(pdf_content) as bytes_io:
        with pdfplumber.open(bytes_io) as pdf:
            for page_content in pdf.pages:
                page = {
                    "text": None,
                    "tables": None,
                    "images": [],
                }  # Will contain info about each page, text+tables
                page["tables"] = page_content.extract_tables()
                page["text"] = page_content.extract_text()
                # print(cntr)
                # cntr+=1
                pages.append(page.copy())

                if page_content.images:
                    for image in page_content.images:
                        try:
                            image_bytes = image["stream"].get_data()
                            # image_bytes = rotateAndFlipImageBytes(image_bytes)
                            if image_bytes:
                                image_description = generateImageDescription(
                                    image_bytes
                                )
                                page["images"].append(image_description)
                        except:
                            pass

    ocr: str = ""

    for page in pages:
        text = page["text"] if page["text"] else ""
        ocr += text + "\n"

        for table in page["tables"]:
            row_text = ""
            for row in table:  # Some parsing for the
                row_text = " | ".join(
                    cell if cell and cell.strip().lower() != "none" else " "
                    for cell in row
                )
                ocr += row_text + "\n" if row_text else ""

        for image_description in page["images"]:
            ocr += image_description
            ocr += "\n"
        ocr += "--\n"

    # with open("test.txt", "w", encoding="utf-8") as f:
    #     f.write(ocr)
    print("ocr finished!")
    return ocr


def extractTextAndTables_(pdf_content: bytes) -> List[str]:
    """Extracts text and tables form pdf

    Args:
        pdf_content (bytes): bytes content of the pdf

    Returns:
        List[str]: list of pages
    """
    pages: List[Dict] = []

    with BytesIO(pdf_content) as bytes_io:
        with pdfplumber.open(bytes_io) as pdf:
            for page_content in pdf.pages:
                page = {
                    "text": None,
                    "tables": None,
                    "images": [],
                }  # Will contain info about each page, text+tables
                page["tables"] = page_content.extract_tables()
                page["text"] = page_content.extract_text()

                pages.append(page.copy())

                if page_content.images:
                    for image in page_content.images:
                        image_bytes = image["stream"].get_data()
                        image_bytes = rotateAndFlipImageBytes(image_bytes)
                        if image_bytes:
                            image_description = generateImageDescription(image_bytes)
                            page["images"].append(image_description)

    pages_parsed: List = []

    for page in pages:
        page_text = ""
        text = page["text"] if page["text"] else ""
        page_text += text + "\n"

        for table in page["tables"]:
            row_text = ""
            for row in table:  # Some parsing for the
                row_text = " | ".join(
                    cell if cell and cell.strip().lower() != "none" else " "
                    for cell in row
                )
                page_text += row_text + "\n" if row_text else ""

        for image_description in page["images"]:
            page_text += image_description
            page_text += "\n"
        pages_parsed.append(page_text)
    return pages_parsed
