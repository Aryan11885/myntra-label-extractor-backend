import fitz
import easyocr
import numpy as np
import cv2
import re

reader = easyocr.Reader(["en"])


def extract_sku_from_pdf(pdf_bytes):

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    page = pdf[0]

    pix = page.get_pixmap(
        matrix=fitz.Matrix(3, 3)
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

    result = reader.readtext(
        img,
        detail=0
    )

    text = "\n".join(result)

    pdf.close()

    products = []

    sku_matches = re.finditer(
        r"([A-Z0-9]+)\(([A-Z0-9\-_]+)\)",
        text
    )

    for match in sku_matches:

        sku = match.group(2)

        size = ""

        size_match = re.search(
            r"_([A-Z0-9]+)$",
            sku
        )

        if size_match:
            size = size_match.group(1)

        products.append(
            {
                "sku": sku,
                "size": size,
                "qty": 1
            }
        )

    return {
        "products": products
    }