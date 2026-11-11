
# 🛡️ InvoiceGuard AI

### Smart Invoice Protection

InvoiceGuard AI is an AI-powered invoice verification prototype designed to help identify suspicious invoice details, detect duplicate submissions, validate invoice calculations, and support safer payment workflows.

## 🚀 Features

- **Invoice Upload:** Upload invoices in PDF, PNG, JPG, or JPEG formats.
- **OCR Extraction:** Extract invoice information using Tesseract OCR.
- **Arithmetic Verification:** Check whether subtotal, tax, additional charges, and total amounts are consistent.
- **Duplicate Detection:** Identify previously reviewed invoices using vendor and invoice number.
- **AI Risk Analysis:** Use Google Gemini to analyze invoice details and highlight potential warning signs.
- **Invoice History:** Store and review invoice records using SQLite.
- **PayPal Integration:** Create and capture PayPal Sandbox payments.
- **Payment History:** View recorded payment transactions and their statuses.

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| AI Analysis | Google Gemini API |
| OCR | Tesseract OCR, Pytesseract |
| PDF Processing | pdf2image, Poppler |
| Database | SQLite |
| Payment Integration | PayPal REST API |
| Image Processing | Pillow |

## 📁 Project Structure

```text
InvoiceGuardAI/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── utils/
│   ├── ai_analyzer.py
│   ├── config.py
│   ├── invoice_checker.py
│   ├── invoice_database.py
│   ├── invoice_extractor.py
│   └── paypal_payment.py
│
└── data/                 # Generated locally
```

The database is generated locally and is not included in the public repository.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/supriyabonkuri18/InvoiceGuardAI.git
cd InvoiceGuardAI
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install OCR system dependencies

On Ubuntu or Debian:

```bash
sudo apt update
sudo apt install -y tesseract-ocr poppler-utils
```

### 5. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Add your own API credentials to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key

PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret

PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

Never upload your actual `.env` file or expose API credentials publicly.

### 6. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 💳 PayPal Integration

InvoiceGuard AI integrates with the PayPal REST API.

The default configuration uses the **PayPal Sandbox environment** for testing payment creation and capture without processing real payments.

Use your own PayPal Sandbox application credentials to test this functionality.

## 🧠 AI Risk Analysis

Google Gemini analyzes extracted invoice information and provides risk-related observations and recommendations.

The AI-generated risk score is a preliminary screening indicator, not a statistically validated fraud probability.

## ⚠️ Important Limitations

- OCR accuracy depends on invoice image quality and formatting.
- Incorrectly extracted information should be manually verified.
- Arithmetic validation checks mathematical consistency, not invoice authenticity.
- Duplicate detection identifies matching vendor and invoice number combinations in the application's database.
- AI risk analysis can produce inaccurate results and should not replace human review.
- PayPal Sandbox transactions are test transactions, not real payments.

**InvoiceGuard AI is a prototype intended for demonstration and evaluation, not a certified financial fraud detection system.**

## 🌱 Future Improvements

- Improved OCR accuracy and field extraction.
- More advanced invoice anomaly detection.
- Additional payment-provider integrations.
- Enhanced vendor verification.
- Production-ready security and deployment.

## 👩‍💻 Built With

Python, Streamlit, Google Gemini, Tesseract OCR, SQLite, and PayPal Sandbox.

---

**InvoiceGuard AI — Making invoice verification smarter.**