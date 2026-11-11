
import re
import pytesseract

from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes


def extract_text_from_invoice(uploaded_file):

    file_bytes = uploaded_file.getvalue()
    extracted_text = ""

    # Read PDF invoices
    if uploaded_file.type == "application/pdf":

        pages = convert_from_bytes(file_bytes)

        for page in pages:
            text = pytesseract.image_to_string(page)
            extracted_text += text + "\n"

    # Read image invoices
    else:

        image = Image.open(BytesIO(file_bytes))
        extracted_text = pytesseract.image_to_string(image)

    return extracted_text


def extract_invoice_details(text):

    details = {}

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

        # 1. Extract vendor name automatically

    ignored_names = {
        "invoice",
        "tax invoice",
        "bill to",
        "ship to",
        "receipt",
        "quotation"
    }

    for line in lines[:8]:

        # Remove invoice header text and invoice number
        cleaned = re.split(
            r"\binvoice\s*(?:number|no\.?|#)\b",
            line,
            flags=re.IGNORECASE
        )[0]

        cleaned = re.sub(
            r"[^A-Za-z0-9 &.-]",
            "",
            cleaned
        ).strip()

        if (
            cleaned
            and cleaned.lower() not in ignored_names
            and re.search(r"[A-Za-z]", cleaned)
            and not re.search(r"\d{3,}", cleaned)
            and len(cleaned) > 3
        ):

            details["vendor"] = cleaned
            break

    # 2. Extract complete invoice number

    invoice_pattern = (
        r"\b[A-Z0-9]+(?:[-/][A-Z0-9]+)+\b"
    )

    for index, line in enumerate(lines):

        if re.search(r"invoice\s*(number|no\.?|#)", line, re.IGNORECASE):

            search_area = " ".join(lines[index:index + 3])

            match = re.search(
                invoice_pattern,
                search_area,
                re.IGNORECASE
            )

            if match:
                details["invoice_number"] = match.group(0)
                break

    # Fallback invoice number extraction

    if "invoice_number" not in details:

        for line in lines:

            match = re.search(
                invoice_pattern,
                line,
                re.IGNORECASE
            )

            if match:
                details["invoice_number"] = match.group(0)
                break

    # 3. Extract dates

    date_pattern = (
        r"\b\d{1,2}[\s/-]+"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?|\d{1,2})"
        r"[\s/-]+\d{2,4}\b"
    )

    def find_date_near_label(label):

        for index, line in enumerate(lines):

            if re.search(label, line, re.IGNORECASE):

                search_area = " ".join(lines[index:index + 3])

                match = re.search(
                    date_pattern,
                    search_area,
                    re.IGNORECASE
                )

                if match:
                    return match.group(0)

        return None

    due_date = find_date_near_label(r"due\s*date")

    if due_date:
        details["due_date"] = due_date

    invoice_date = find_date_near_label(r"invoice\s*date")

    if invoice_date:
        details["invoice_date"] = invoice_date

    # Fallback: use an unlabelled date as invoice date
    if "invoice_date" not in details:

        all_dates = re.findall(
            date_pattern,
            text,
            re.IGNORECASE
        )

        if all_dates:

            for found_date in all_dates:

                if found_date != due_date:
                    details["invoice_date"] = found_date
                    break

    # 4. Extract monetary amounts

    amount_pattern = r"(?<!\d)[^\d\n]{0,5}(\d[\d,]*(?:\.\d{1,2})?)(?!\d)"

    labels = {
        "subtotal": r"\bsubtotal\b",
        "tax": r"\b(?:tax|gst|vat)\b",
        "extra_charges": r"\b(?:extra charges|additional charges|delivery|handling|shipping)\b",
        "total": r"\b(?:grand total|total due|total amount|invoice total|total)\b"
    }

    # First try extracting amounts on the same line as labels

    for field, label_pattern in labels.items():

        for index, line in enumerate(lines):

            if re.search(label_pattern, line, re.IGNORECASE):

                # Avoid treating item descriptions as amounts
                label_match = re.search(
                    label_pattern,
                    line,
                    re.IGNORECASE
                )

                remaining = line[label_match.end():]

                # Remove percentage rates such as (18%)
                remaining = re.sub(
                    r"\(?\s*\d+(?:\.\d+)?\s*%\s*\)?",
                    " ",
                    remaining
                )

                amount_match = re.search(
                    amount_pattern,
                    remaining
                )

                if amount_match:

                    details[field] = float(
                        amount_match.group(1).replace(",", "")
                    )
                    break

    # Fallback for OCR where all labels appear before their amounts.
    # Associate the trailing amounts with the ordered labels
    # only when their counts match exactly.

    missing_fields = [
        field for field in labels
        if field not in details
    ]

    if missing_fields:

        last_label_position = -1

        for index, line in enumerate(lines):

            if any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in labels.values()
            ):
                last_label_position = index

        if last_label_position >= 0:

            trailing_text = "\n".join(
                lines[last_label_position + 1:]
            )

            amounts = re.findall(
                r"(?<!\w)(\d[\d,]*\.\d{2})(?!\w)",
                trailing_text
            )

            # Use this fallback only when the number
            # of amounts matches the number of missing fields.
            if len(amounts) >= len(missing_fields):

                amounts = amounts[-len(missing_fields):]

                for field, amount in zip(missing_fields, amounts):

                    details[field] = float(
                        amount.replace(",", "")
                    )

    return {
        "raw_text": text,
        "details": details
    }