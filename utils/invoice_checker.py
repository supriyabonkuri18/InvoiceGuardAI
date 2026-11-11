
from decimal import Decimal


def check_invoice(subtotal, tax, extra_charges, total):

    issues = []

    subtotal = Decimal(str(subtotal))
    tax = Decimal(str(tax))
    extra_charges = Decimal(str(extra_charges))
    total = Decimal(str(total))

    # Calculate the expected invoice total
    expected_total = subtotal + tax + extra_charges

    # Check arithmetic accuracy
    difference = total - expected_total

    if abs(difference) > Decimal("0.01"):

        issues.append({
            "type": "Calculation Error",
            "severity": "High",
            "message": (
                f"The invoice total is ₹{total}, "
                f"but the calculated total is ₹{expected_total}."
            ),
            "difference": float(difference)
        })

    else:

        issues.append({
            "type": "Calculation Check",
            "severity": "Pass",
            "message": "The invoice total matches the calculated amount."
        })

    return {
        "expected_total": float(expected_total),
        "invoice_total": float(total),
        "issues": issues,
        "is_valid": abs(difference) <= Decimal("0.01")
    }


def check_duplicate(vendor, invoice_number, previous_invoices):

    for invoice in previous_invoices:

        if (
            vendor.strip().lower() == invoice["vendor"].strip().lower()
            and invoice_number.strip().lower()
            == invoice["invoice_number"].strip().lower()
        ):

            return {
                "duplicate": True,
                "message": "A possible duplicate invoice was found."
            }

    return {
        "duplicate": False,
        "message": "No matching invoice was found in the stored records."
    }