import fitz
import re


def extract_sku_details(pdf_bytes):

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    page = pdf[0]

    text = page.get_text()

    result = {
        "sku": "",
        "size": "",
        "qty": "",
        "product_name": "",
        "invoice_number": "",
        "order_number": ""
    }

    invoice_match = re.search(
        r"Invoice Number:\s*([A-Z0-9]+)",
        text
    )

    if invoice_match:
        result["invoice_number"] = invoice_match.group(1)

    order_match = re.search(
        r"Order Number:\s*([0-9\-]+)",
        text
    )

    if order_match:
        result["order_number"] = order_match.group(1)

    qty_match = re.search(
        r"\n(\d+)\s+Rs",
        text
    )

    if qty_match:
        result["qty"] = qty_match.group(1)

    sku_match = re.search(
        r"\(([A-Z0-9\-_]+)\)",
        text
    )

    if sku_match:

        sku = sku_match.group(1)

        result["sku"] = sku

        size_match = re.search(
            r"_([0-9]+)$",
            sku
        )

        if size_match:
            result["size"] = size_match.group(1)

    product_match = re.search(
        r"\)\s*-\s*(.*?)HSN:",
        text,
        re.DOTALL
    )

    if product_match:

        result["product_name"] = (
            product_match.group(1)
            .replace("\n", " ")
            .strip()
        )

    pdf.close()

    return result