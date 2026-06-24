from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import tempfile
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
   allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Myntra Label Extractor Running"
    }


@app.post("/extract-label")
async def extract_label(file: UploadFile = File(...)):

    pdf_bytes = await file.read()

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    best_page = None
    highest_barcode_count = -1

    for page_number in range(len(pdf)):

        page = pdf[page_number]

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        img = np.frombuffer(
            pix.samples,
            dtype=np.uint8
        ).reshape(
            pix.height,
            pix.width,
            pix.n
        )

        if pix.n == 4:
            img = cv2.cvtColor(
                img,
                cv2.COLOR_RGBA2RGB
            )

        barcodes = decode(img)

        barcode_count = len(barcodes)

        print(
            f"Page {page_number} -> {barcode_count} barcode(s)"
        )

        if barcode_count > highest_barcode_count:
            highest_barcode_count = barcode_count
            best_page = page_number

    if best_page is None:
        return {
            "success": False,
            "message": "No label page found"
        }

    output_pdf = fitz.open()

    output_pdf.insert_pdf(
        pdf,
        from_page=best_page,
        to_page=best_page
    )

    output_path = os.path.join(
        tempfile.gettempdir(),
        f"label_{file.filename}"
    )

    output_pdf.save(output_path)

    output_pdf.close()
    pdf.close()

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"label_{file.filename}"
    )