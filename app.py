
from utils.invoice_checker import check_invoice, check_duplicate
from utils.ai_analyzer import analyze_invoice
from utils.invoice_database import get_all_invoices
import base64
import streamlit.components.v1 as components
import streamlit as st
from datetime import date, datetime
from utils.invoice_database import (
    initialize_database,
    find_duplicate,
    save_invoice,
    save_payment,
    get_all_payments,
    get_all_invoices,
    update_invoice_arithmetic_status
)
from utils.ai_analyzer import analyze_invoice
from utils.invoice_extractor import (
    extract_text_from_invoice,
    extract_invoice_details
)
import hashlib
from utils.paypal_payment import create_paypal_order, capture_paypal_order
initialize_database()

# Page configuration
st.set_page_config(
    page_title="InvoiceGuard AI",
    page_icon="🛡️",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.stApp {
    background-color: #0e1424;
    color: white;
}
.block-container {
    padding-top: 2rem;
}
[data-testid="stMetric"] {
    background-color: #19243a;
    padding: 20px;
    border-radius: 12px;
}
div.stButton > button,
[data-testid="stFormSubmitButton"] button {
    background-color: #3978f6 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    background-color: #245ac5 !important;
    color: white !important;
}

[data-testid="stFormSubmitButton"] button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    opacity: 1 !important;
    min-height: 48px !important;
}

[data-testid="stFormSubmitButton"] button *,
[data-testid="stFormSubmitButton"] button p {
    color: #ffffff !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 700 !important;
}


/* Make all form labels bright and readable */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stRadio label,
[data-testid="stFileUploader"] label {
    color: #ffffff !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* Improve input field visibility */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: #19243a !important;
    color: #ffffff !important;
    border: 1px solid #64748b !important;
    border-radius: 8px !important;
}

/* Improve placeholder visibility */
.stTextInput input::placeholder {
    color: #cbd5e1 !important;
    opacity: 1 !important;
}

/* Improve file uploader appearance */
[data-testid="stFileUploader"] {
    background-color: #19243a !important;
    border: 1px dashed #64748b !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* Make general text more readable */
.stApp,
.stApp p,
.stApp span {
    color: #f1f5f9;
}

/* Your existing CSS */

/* Make general text more readable */
.stApp,
.stApp p,
.stApp span {
    color: #f1f5f9;
}

/* ADD THE NEW CSS HERE */

/* Make Streamlit widget labels clearly visible */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
.stTextInput label,
.stNumberInput label,
.stDateInput label,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label * {
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

/* Improve section headings */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #ffffff !important;
}

/* FIX SIDEBAR TEXT VISIBILITY */
[data-testid="stSidebar"] {
    background-color: #f1f5f9 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #1e293b !important;
    opacity: 1 !important;
}

/* Sidebar navigation text */
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [role="radiogroup"] label * {
    color: #1e293b !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* Sidebar status message */
[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #166534 !important;
}

/* INVOICEGUARD - DATE INPUT DARK THEME */

[data-testid="stDateInputField"] {
    background-color: #1a2438 !important;
}

[data-testid="stDateInputFieldsScroller"] {
    background-color: #1a2438 !important;
    border: 1px solid #344563 !important;
    border-radius: 8px !important;
}

[data-testid="stDateInputField"] [role="group"] {
    background-color: #1a2438 !important;
    color: #ffffff !important;
    border: none !important;
}

[data-testid="stDateInputField"] [role="spinbutton"] {
    color: #ffffff !important;
    background-color: transparent !important;
}

[data-testid="stDateInputField"] span {
    color: #ffffff !important;
}

[data-testid="stDateInputField"] svg {
    color: #60a5fa !important;
    fill: #60a5fa !important;
}

</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛡️ InvoiceGuard AI")
st.sidebar.caption("Smart Invoice Protection")

payment_return = st.query_params.get("payment")

default_page = (
    "Payment History"
    if payment_return in ["success", "cancel"]
    else "Dashboard"
)

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Review Invoice", "Payment History"],
    index=["Dashboard", "Review Invoice", "Payment History"].index(default_page)
)

st.sidebar.divider()
st.sidebar.success("System Status: Prototype Active")

# Dashboard
if page == "Dashboard":

    st.title("🛡️ InvoiceGuard AI")
    st.subheader("AI-Powered Invoice Verification & Secure Payments")

    st.write(
        "Detect possible invoice errors, identify suspicious charges "
        "and review payments before proceeding."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Invoices Reviewed", "0")
    col2.metric("Potential Issues", "0")
    col3.metric("Payments Processed", "0")

    st.divider()

    st.subheader("How InvoiceGuard Works")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 📄")
        st.markdown("**1. Upload Invoice**")
        st.write("Upload an invoice for verification.")

    with c2:
        st.markdown("### 🤖")
        st.markdown("**2. AI Analysis**")
        st.write("Identify possible errors and unexpected charges.")

    with c3:
        st.markdown("### 💳")
        st.markdown("**3. Secure Payment**")
        st.write("Review the invoice and approve a PayPal test payment.")

    st.info("AI analysis and PayPal integration are being developed.")

     # Invoice Review
elif page == "Review Invoice":

    st.title("📄 Invoice Review")
    st.write("Upload an invoice and verify its details.")

    uploaded_file = st.file_uploader(
    "Upload Invoice",
    type=["pdf", "png", "jpg", "jpeg"]
)

    # Display uploaded invoice
    if uploaded_file is not None:

        st.success("✅ Invoice uploaded successfully!")

        st.write(f"📄 **File name:** {uploaded_file.name}")

        file_size = uploaded_file.size / 1024
        st.write(f"📦 **File size:** {file_size:.2f} KB")

        st.subheader("📑 Invoice Preview")

        if uploaded_file.type == "application/pdf":

            pdf_data = base64.b64encode(
                uploaded_file.getvalue()
            ).decode("utf-8")

            pdf_display = f"""
            <iframe
                src="data:application/pdf;base64,{pdf_data}"
                width="100%"
                height="600"
                type="application/pdf">
            </iframe>
            """

            components.html(
                pdf_display,
                height=620,
                scrolling=True
            )

        else:
            st.image(
                uploaded_file,
                caption="Uploaded Invoice",
                use_container_width=True
            )

        st.divider()

        def convert_ocr_date(date_string):

            if not date_string:
                return date.today()

            formats = [
                "%d %B %Y",
                "%d %b %Y",
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%Y-%m-%d",
                "%Y%m%d"
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue

            return date.today()
                # OCR: Automatically read uploaded invoices
        if uploaded_file is not None:

            file_signature = hashlib.sha256(
                uploaded_file.getvalue()
            ).hexdigest()

            if st.session_state.get("ocr_file_signature") != file_signature:

                st.session_state["ocr_file_signature"] = file_signature

                with st.spinner("🤖 Reading invoice using OCR..."):

                    try:
                        extracted_text = extract_text_from_invoice(uploaded_file)

                        extraction_result = extract_invoice_details(extracted_text)

                        extracted_details = extraction_result["details"]

                        st.session_state["vendor_input"] = extracted_details.get(
                            "vendor", ""
                        )

                        st.session_state["invoice_date_input"] = convert_ocr_date(
                            extracted_details.get("invoice_date")
                        )

                        st.session_state["due_date_input"] = convert_ocr_date(
                            extracted_details.get("due_date")
                        )

                        st.session_state["invoice_number_input"] = extracted_details.get(
                            "invoice_number", ""
                        )

                        st.session_state["subtotal_input"] = float(
                            extracted_details.get("subtotal", 0.0) or 0.0
                        )

                        st.session_state["tax_input"] = float(
                            extracted_details.get("tax", 0.0) or 0.0
                        )

                        st.session_state["extra_charges_input"] = float(
                            extracted_details.get("extra_charges", 0.0) or 0.0
                        )

                        st.session_state["total_input"] = float(
                            extracted_details.get("total", 0.0) or 0.0
                        )

                        if extracted_details:
                            st.success("✅ Invoice details extracted!")
                        else:
                            st.warning("Please enter invoice details manually.")

                    except Exception as e:
                        st.error(f"OCR extraction failed: {e}")

    with st.form("invoice_form"):

        st.subheader("Invoice Details")

        vendor = st.text_input(
            "Vendor / Company Name",
            key="vendor_input"
        )

        invoice_number = st.text_input(
            "Invoice Number",
            key="invoice_number_input"
        )

        col1, col2 = st.columns(2)

        with col1:

            subtotal = st.number_input(
                "Subtotal (₹)",
                min_value=0.0,
                step=100.0,
                key="subtotal_input"
            )

            tax = st.number_input(
                "Tax (₹)",
                min_value=0.0,
                step=10.0,
                key="tax_input"
            )

            extra_charges = st.number_input(
                "Extra Charges (₹)",
                min_value=0.0,
                step=10.0,
                key="extra_charges_input"
            )

        with col2:

            total = st.number_input(
                "Total Invoice Amount (₹)",
                min_value=0.0,
                step=100.0,
                key="total_input"
            )

            invoice_date = st.date_input(
                "Invoice Date",
                key="invoice_date_input"
            )

            due_date = st.date_input(
                "Payment Due Date",
                key="due_date_input"
            )

        submitted = st.form_submit_button(
            "🔍 VERIFY INVOICE",
            use_container_width=True,
            type="primary"
        )

        if submitted:

            if not vendor.strip() or not invoice_number.strip():
                st.error("Please enter vendor name and invoice number.")

            elif uploaded_file is None:
                st.error("Please upload an invoice.")

            elif total <= 0:
                st.error("Please enter a valid invoice total.")

            else:

                duplicate_record = find_duplicate(
                    vendor,
                    invoice_number
                )

                result = check_invoice(
                    subtotal,
                    tax,
                    extra_charges,
                    total
                )

                previous_invoices = get_all_invoices()

                invoice_data = {
                    "vendor": vendor,
                    "invoice_number": invoice_number,
                    "invoice_date": str(invoice_date),
                    "subtotal": subtotal,
                    "tax": tax,
                    "extra_charges": extra_charges,
                    "amount": total,
                    "due_date": str(due_date),
                    "filename": uploaded_file.name,
                    "arithmetic_valid": result["is_valid"]
                }

                if duplicate_record:
                    update_invoice_arithmetic_status(
                        vendor,
                        invoice_number,
                        result["is_valid"]
                    )

                    st.session_state["duplicate_result"] = {
                        "duplicate": True,
                        "previous_amount": duplicate_record[1],
                        "review_date": duplicate_record[2]
                   }

                else:
                    saved = save_invoice(invoice_data)

                    st.session_state["duplicate_result"] = {
                        "duplicate": not saved,
                        "previous_amount": None,
                        "review_date": None
                    }

                st.session_state["invoice"] = invoice_data

                 # Gemini AI invoice risk analysis
                with st.spinner("🤖 Gemini AI is analyzing your invoice..."):

                    ai_result = analyze_invoice(
                    invoice=invoice_data,
                    previous_invoices=previous_invoices,
                    arithmetic_result=result,
                    duplicate_detected=bool(duplicate_record)
                )

            st.session_state["ai_result"] = ai_result

            st.session_state["verification_result"] = result

    # Display verification results
    if "verification_result" in st.session_state:

        result = st.session_state["verification_result"]

        st.divider()


        duplicate_info = st.session_state.get(
            "duplicate_result", {}
        )

        if duplicate_info.get("duplicate"):

            st.warning("⚠️ POSSIBLE DUPLICATE INVOICE DETECTED!")

            st.write(
                "This vendor and invoice number combination "
                "has already been reviewed."
            )

            if duplicate_info["previous_amount"] is not None:
                st.write(
                    f"Previous invoice amount: "
                    f"₹{duplicate_info['previous_amount']:,.2f}"
                )

            st.error(
                "Please review this invoice before proceeding with payment."
            )

        else:
            st.success(
                "New invoice recorded successfully in the database."
            )

        st.subheader("🛡️ Invoice Verification Results")

        if result["is_valid"]:
            st.success("No arithmetic mismatch detected.")

        else:
            st.error("Potential invoice calculation error detected!")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Invoice Total",
            f"₹{result['invoice_total']:,.2f}"
        )

        col2.metric(
            "Expected Total",
            f"₹{result['expected_total']:,.2f}"
        )

        col3.metric(
            "Difference",
            f"₹{abs(result['invoice_total'] - result['expected_total']):,.2f}"
        )

        for issue in result["issues"]:

            if issue["severity"] == "High":
                st.error(issue["message"])

            else:
                st.success(issue["message"])

        st.info(
            "This check verifies arithmetic only. "
            "It does not establish whether an invoice is fraudulent."
        )

                # Gemini AI Risk Analysis
        ai_result = st.session_state.get("ai_result", {})

        st.divider()
        st.subheader("🤖 Gemini AI Risk Analysis")

        if ai_result.get("available"):

            risk_level = ai_result["risk_level"]

            if risk_level == "High":
                st.error(f"🚨 Risk Level: {risk_level}")
            elif risk_level == "Medium":
                st.warning(f"⚠️ Risk Level: {risk_level}")
            else:
                st.success(f"✅ Risk Level: {risk_level}")

            st.metric(
                "AI Risk Score",
                f"{ai_result['risk_score']}/100"
            )

            st.write(ai_result["summary"])

            st.markdown("### 🔴 Genuine Risk Indicators")

            indicators = ai_result.get("indicators", [])

            if indicators:
                for item in indicators:
                    st.write(f"- {item}")
            else:
                st.success("No significant risk indicators identified.")

            st.markdown("### 🟡 Neutral Observations")

            observations = ai_result.get("observations", [])

            if observations:
                for item in observations:
                    st.write(f"- {item}")
            else:
                st.write("No additional observations.")

            st.markdown("### 💡 Recommended Actions")

            recommendations = ai_result.get("recommendations", [])

            if recommendations:
                for item in recommendations:
                    st.write(f"- {item}")
            else:
                st.write("No additional actions recommended.")

            st.caption(
                "AI-generated screening assessment. "
                "This score is not proof of fraud."
            )

        else:
            st.warning("Gemini AI analysis is currently unavailable.")
            st.caption(ai_result.get("error", "Unknown AI error"))

elif page == "Payment History":

    import streamlit as st
    from datetime import datetime

    st.title("💳 Payment History")

    # Handle PayPal return after buyer approval
    payment_status = st.query_params.get("payment")
    order_id = st.query_params.get("token")

    if payment_status == "success" and order_id:
        if st.session_state.get("captured_order_id") != order_id:
            try:
                capture = capture_paypal_order(order_id)

                if capture["status"] == "COMPLETED":

                    payment_record = {
                        "order_id": capture["order_id"],
                        "capture_id": capture["capture_id"],
                        "invoice_number": capture["invoice_number"],
                        "amount": capture["amount"],
                        "currency": capture["currency"],
                        "status": capture["status"]
                    }
                    saved = save_payment(payment_record)

                    if saved:
                        st.success("Payment saved to database!")
                    else:
                        st.info("Payment already exists in database.")

                st.session_state["captured_order_id"] = order_id
                st.session_state["paypal_capture"] = capture

            except Exception as e:
                st.error(f"Payment capture failed: {e}")

    if payment_status == "cancel":
        st.warning("PayPal payment was cancelled.")

        st.divider()
    st.subheader("🧾 Pay for a Verified Invoice")

    saved_invoices = get_all_invoices()

    if not saved_invoices:

        st.info("No reviewed invoices found. Please review an invoice first.")

    else:

        invoice_options = {
            f"{invoice['vendor']} — {invoice['invoice_number']} (₹{invoice['amount']:,.2f})": invoice
            for invoice in saved_invoices
        }

        selected_label = st.selectbox(
            "Select an invoice",
            list(invoice_options.keys())
        )

        selected_invoice = invoice_options[selected_label]
        invoice_number = selected_invoice["invoice_number"]

        # Clear an old PayPal order when the selected invoice changes
        if st.session_state.get("invoice_paypal_invoice") != invoice_number:

            st.session_state.pop("invoice_paypal_order", None)
            st.session_state["invoice_paypal_invoice"] = invoice_number

        st.write("Vendor:", selected_invoice["vendor"])
        st.write("Invoice Number:", invoice_number)
        st.write(f"Original Invoice Amount: ₹{selected_invoice['amount']:,.2f}")

        if not bool(selected_invoice.get("arithmetic_valid", 0)):

            st.error(
                "Payment blocked: This invoice has not passed arithmetic verification."
            )

        else:

            completed_payments = [
                payment for payment in get_all_payments()
                if payment.get("invoice_number") == invoice_number
                and payment.get("status") == "COMPLETED"
            ]

            if completed_payments:

                st.success("This invoice already has a completed payment.")

            else:

                st.success("Arithmetic verification passed.")

                st.caption(
                    "Enter a separate USD amount for Sandbox testing. "
                    "This does not convert or settle the original INR invoice."
                )

                usd_amount = st.number_input(
                    "Sandbox Payment Amount (USD)",
                    min_value=0.01,
                    value=1.00,
                    step=0.01,
                    key="invoice_usd_amount"
                )

                if st.button("💳 Create Invoice-Linked PayPal Order"):

                    try:

                        order = create_paypal_order(
                            amount=usd_amount,
                            invoice_number=invoice_number,
                            return_url="http://localhost:8501/?payment=success",
                            cancel_url="http://localhost:8501/?payment=cancel",
                            currency="USD"
                        )

                        st.session_state["invoice_paypal_order"] = order
                        st.session_state["invoice_paypal_invoice"] = invoice_number

                        st.success("Invoice-linked PayPal order created!")

                    except Exception as e:

                        st.error(f"PayPal Error: {e}")

                if (
                    "invoice_paypal_order" in st.session_state
                    and st.session_state.get("invoice_paypal_invoice") == invoice_number
                ):

                    invoice_order = st.session_state["invoice_paypal_order"]

                    st.write("PayPal Order ID:", invoice_order["order_id"])
                    st.write("Status:", invoice_order["status"])

                    st.link_button(
                        "Proceed to Invoice Payment",
                        invoice_order["approval_url"]
                    )

    st.info("PayPal Sandbox Payment Testing")

    st.write("Generate a test payment of $1.00 USD.")

    if st.button("💰 Create $1.00 PayPal Test Order"):

        try:
            invoice_number = (
                "IG-TEST-" + datetime.now().strftime("%Y%m%d%H%M%S")
            )

            order = create_paypal_order(
                amount=1.00,
                invoice_number=invoice_number,
                return_url="http://localhost:8501/?payment=success",
                cancel_url="http://localhost:8501/?payment=cancel"
            )

            st.session_state["paypal_order"] = order

            st.success("PayPal order created successfully!")

        except Exception as e:
            st.error(f"PayPal Error: {e}")

    if "paypal_order" in st.session_state:

        order = st.session_state["paypal_order"]

        st.write("Order ID:", order["order_id"])
        st.write("Status:", order["status"])

        st.link_button(
            "Proceed to PayPal Checkout",
            order["approval_url"]
        )

     # Display captured payment details
    if "paypal_capture" in st.session_state:

        capture = st.session_state["paypal_capture"]

        st.divider()
        st.subheader("✅ PayPal Payment Result")

        st.success(f"Payment Status: {capture['status']}")

        st.write("Order ID:", capture["order_id"])
        st.write("Capture ID:", capture["capture_id"])

        st.divider()
    st.subheader("📚 Saved Payment Transactions")

    payments = get_all_payments()

    if payments:

        st.success(f"{len(payments)} payment record(s) found.")

        for payment in payments:

            invoice_label = (
                payment.get("invoice_number")
                or "Standalone Test Payment"
            )

            with st.expander(
                f"💳 {payment['currency']} {payment['amount']:.2f} | "
                f"{payment['status']} | {invoice_label}"
            ):

                st.write("Order ID:", payment["order_id"])
                st.write("Capture ID:", payment["capture_id"])
                st.write("Invoice Number:", invoice_label)
                st.write("Payment Date:", payment["payment_date"])

    else:
        st.info("No saved payment transactions yet.")