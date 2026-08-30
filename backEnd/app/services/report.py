from fpdf import FPDF
from datetime import datetime


def generate_pdf_report(receipts: list, month: str, user_name: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # כותרת
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, f"ReceiptWise - Expense Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Period: {month}  |  User: {user_name}", ln=True, align="C")
    pdf.ln(6)

    # כותרות טבלה
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    headers = ["Date", "Vendor", "Category", "Amount"]
    widths = [30, 70, 40, 50]
    for header, w in zip(headers, widths):
        pdf.cell(w, 8, header, border=1, fill=True, align="C")
    pdf.ln()

    # שורות
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    total = 0.0
    fill = False

    for r in receipts:
        pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(widths[0], 7, str(r.date or ""), border=1, fill=True)
        pdf.cell(widths[1], 7, str(r.vendor or "Unknown")[:35], border=1, fill=True)
        pdf.cell(widths[2], 7, str(r.category.value if r.category else ""), border=1, fill=True, align="C")
        amount_str = f"{r.currency} {r.amount:.2f}" if r.amount else "-"
        pdf.cell(widths[3], 7, amount_str, border=1, fill=True, align="R")
        pdf.ln()
        fill = not fill
        if r.amount:
            total += r.amount

    # סה"כ
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Total: ILS {total:.2f}", ln=True, align="R")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")

    return bytes(pdf.output())
