import os
import json
import pdfplumber
import pytesseract
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import openai

# Set OpenAI API key
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY


def extract_text_from_pdf(file_path):
    """Extract text from PDF using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
        return ""


def extract_text_from_image(image_file):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def extract_with_openai(text, document_type="proforma"):
    """Use OpenAI to extract structured data from text"""
    if not settings.OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured"}

    try:
        if document_type == "proforma":
            prompt = f"""
            Extract the following information from this proforma invoice/quotation:
            - Vendor/Seller name
            - Vendor contact information
            - Items (name, quantity, unit price)
            - Total amount
            - Currency
            - Terms and conditions
            - Payment terms
            - Delivery terms

            Text:
            {text}

            Return the data as a JSON object.
            """
        elif document_type == "receipt":
            prompt = f"""
            Extract the following information from this receipt:
            - Seller/Vendor name
            - Items purchased (name, quantity, price)
            - Total amount
            - Currency
            - Date of purchase
            - Receipt number or invoice number

            Text:
            {text}

            Return the data as a JSON object.
            """
        else:
            return {"error": "Unknown document type"}

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from documents. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content

        # Try to parse the JSON response
        try:
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.split("```json")[1]
            if content.startswith("```"):
                content = content.split("```")[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]

            data = json.loads(content.strip())
            return data
        except json.JSONDecodeError:
            return {"raw_response": content}

    except Exception as e:
        print(f"Error with OpenAI extraction: {e}")
        return {"error": str(e)}


def extract_proforma_data(proforma_file):
    """Extract data from proforma document"""
    file_path = proforma_file.path
    file_extension = os.path.splitext(file_path)[1].lower()

    # Extract text based on file type
    if file_extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        text = extract_text_from_image(file_path)
    else:
        return {"error": "Unsupported file format"}

    if not text.strip():
        return {"error": "No text could be extracted from the document"}

    # Use OpenAI to extract structured data
    extracted_data = extract_with_openai(text, "proforma")
    extracted_data['raw_text'] = text[:500]  # Store first 500 chars of raw text

    return extracted_data


def generate_purchase_order(purchase_request):
    """Generate a Purchase Order document from approved request"""
    if not purchase_request.proforma_data:
        return None, {"error": "No proforma data available"}

    proforma_data = purchase_request.proforma_data

    # Create PO data structure
    po_data = {
        "po_number": f"PO-{purchase_request.id}-{purchase_request.created_at.strftime('%Y%m%d')}",
        "request_id": purchase_request.id,
        "request_title": purchase_request.title,
        "created_at": purchase_request.created_at.isoformat(),
        "approved_at": purchase_request.updated_at.isoformat(),
        "vendor": proforma_data.get("vendor", "Unknown"),
        "items": proforma_data.get("items", []),
        "total_amount": float(purchase_request.amount),
        "currency": proforma_data.get("currency", "USD"),
        "terms": proforma_data.get("terms", ""),
        "payment_terms": proforma_data.get("payment_terms", ""),
        "delivery_terms": proforma_data.get("delivery_terms", ""),
        "status": "issued"
    }

    # Generate PO document (simple text format for now)
    po_content = f"""
    PURCHASE ORDER
    ============================================
    PO Number: {po_data['po_number']}
    Date: {po_data['created_at']}

    Request: {po_data['request_title']}

    VENDOR INFORMATION
    ============================================
    {po_data['vendor']}

    ITEMS
    ============================================
    """

    if isinstance(po_data['items'], list):
        for item in po_data['items']:
            if isinstance(item, dict):
                po_content += f"\n{item.get('name', 'Item')}: {item.get('quantity', 1)} x {item.get('unit_price', 0)} = {item.get('total', 0)}"

    po_content += f"""

    TOTAL: {po_data['currency']} {po_data['total_amount']}

    TERMS & CONDITIONS
    ============================================
    {po_data['terms']}

    Payment Terms: {po_data['payment_terms']}
    Delivery Terms: {po_data['delivery_terms']}
    """

    # Save PO as a file
    po_filename = f"PO_{purchase_request.id}_{purchase_request.created_at.strftime('%Y%m%d')}.txt"
    po_file = ContentFile(po_content.encode('utf-8'))
    po_file.name = po_filename

    return po_file, po_data


def validate_receipt(receipt_file, po_data):
    """Validate receipt against Purchase Order"""
    if not po_data:
        return {}, {"status": "error", "message": "No PO data available for comparison"}

    file_path = receipt_file.path
    file_extension = os.path.splitext(file_path)[1].lower()

    # Extract text from receipt
    if file_extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        text = extract_text_from_image(file_path)
    else:
        return {}, {"status": "error", "message": "Unsupported file format"}

    if not text.strip():
        return {}, {"status": "error", "message": "No text could be extracted from receipt"}

    # Extract receipt data
    receipt_data = extract_with_openai(text, "receipt")

    # Compare receipt with PO
    validation_result = {
        "status": "pending",
        "discrepancies": [],
        "matches": [],
    }

    # Validate vendor/seller
    po_vendor = po_data.get("vendor", "").lower()
    receipt_vendor = str(receipt_data.get("seller", "")).lower()

    if po_vendor and receipt_vendor:
        if po_vendor in receipt_vendor or receipt_vendor in po_vendor:
            validation_result["matches"].append("Vendor name matches")
        else:
            validation_result["discrepancies"].append({
                "field": "vendor",
                "po_value": po_data.get("vendor"),
                "receipt_value": receipt_data.get("seller"),
                "message": "Vendor name mismatch"
            })

    # Validate total amount
    po_total = float(po_data.get("total_amount", 0))
    receipt_total = float(receipt_data.get("total_amount", 0)) if receipt_data.get("total_amount") else 0

    if po_total > 0 and receipt_total > 0:
        if abs(po_total - receipt_total) < 0.01:  # Allow small floating point differences
            validation_result["matches"].append("Total amount matches")
        else:
            validation_result["discrepancies"].append({
                "field": "total_amount",
                "po_value": po_total,
                "receipt_value": receipt_total,
                "message": f"Amount mismatch: PO={po_total}, Receipt={receipt_total}"
            })

    # Validate items (basic check)
    po_items = po_data.get("items", [])
    receipt_items = receipt_data.get("items", [])

    if len(po_items) != len(receipt_items):
        validation_result["discrepancies"].append({
            "field": "items_count",
            "po_value": len(po_items),
            "receipt_value": len(receipt_items),
            "message": f"Number of items mismatch: PO has {len(po_items)}, Receipt has {len(receipt_items)}"
        })

    # Determine overall status
    if len(validation_result["discrepancies"]) == 0:
        validation_result["status"] = "validated"
        validation_result["message"] = "Receipt validated successfully"
    else:
        validation_result["status"] = "discrepancy_found"
        validation_result["message"] = f"Found {len(validation_result['discrepancies'])} discrepancies"

    receipt_data['validation_performed_at'] = purchase_request.updated_at.isoformat() if hasattr(purchase_request, 'updated_at') else None

    return receipt_data, validation_result
