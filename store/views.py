from rest_framework import viewsets
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from io import BytesIO
import os
from .models import Product, Invoice
from .serializers import ProductSerializer, InvoiceSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

def draw_footer(canvas, doc):
    canvas.saveState()

    footer_y = 50
    page_width = doc.pagesize[0]

    # Light orange background (very low opacity feel)
    canvas.setFillColorRGB(1, 0.95, 0.90)  # soft light orange
    canvas.rect(0, 0, page_width, 80, stroke=0, fill=1)

    canvas.setFillColorRGB(0, 0, 0)
    canvas.setFont("Helvetica", 10)

    # LEFT SIDE
    canvas.drawString(40, footer_y, "DAPUR NAPIT")
    canvas.drawString(40, footer_y - 14, "Ciledug, Tangerang")
    canvas.drawString(40, footer_y - 28, "")

    # RIGHT SIDE
    canvas.drawString(350, footer_y, "Bank Mandiri")
    canvas.drawString(350, footer_y - 14, "Denny Herdian")
    canvas.drawString(350, footer_y - 28, "No Rek:")

    canvas.restoreState()

def format_rupiah(value):
    return f"Rp{value:,.0f}".replace(",", ".")


def generate_invoice_pdf(request, pk):
    invoice = Invoice.objects.get(pk=pk)

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=90,
    )

    styles = getSampleStyleSheet()
    elements = []

    LIGHT_ORANGE = colors.HexColor("#FFE5CC")

    # -------------------------
    # HEADER (LOGO + INVOICE INFO)
    # -------------------------

    logo_path = os.path.join("media", "logo.png")
    logo = Image(logo_path, width=3.5 * cm, height=3.5 * cm)

    invoice_title = Paragraph(
        "<b><font size=24>INVOICE</font></b>",
        styles["Normal"]
    )

    invoice_meta = Table([
        ["Invoice #:", invoice.invoice_number],
        ["Date:", str(invoice.date)],
        ["Customer:", invoice.customer_name],
    ])

    invoice_meta.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    right_section = Table([
        [invoice_title],
        [Spacer(1, 6)],
        [invoice_meta]
    ])

    right_section.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 0)
    ]))

    header_table = Table(
        [
            [
                logo,
                Paragraph("<b><font size=20>INVOICE</font></b>", styles["Normal"]),
            ],
            [
                "",
                Paragraph(
                    f"<font color='#f28c28'><b>{invoice.invoice_number}</b></font>",
                    styles["Normal"]
                ),
            ],
        ],
        colWidths=[4 * cm, 14 * cm],
    )

    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ])
    )

    elements.append(header_table)

    elements.append(
        Table(
            [[""]],
            colWidths=[18 * cm],
            style=[
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.lightgrey),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ],
        )
    )

    elements.append(Spacer(1, 30))

    # -------------------------
    # BILL TO SECTION
    # -------------------------

    bill_to_title = Paragraph(
        "<b><font size=12>Bill To</font></b>",
        styles["Normal"]
    )

    bill_to_customer = Paragraph(
        f"{invoice.customer_name}",
        styles["Normal"]
    )

    bill_to_table = Table(
        [
            [bill_to_title],
            [bill_to_customer]
        ],
        colWidths=[18 * cm]
    )

    bill_to_section = Table(
        [
            [
                Paragraph("<b>Bill To</b>", styles["Normal"]),
                Paragraph("<b>Date</b>", styles["Normal"]),
            ],
            [
                Paragraph(invoice.customer_name, styles["Normal"]),
                Paragraph(invoice.date.strftime("%Y-%m-%d"), styles["Normal"]),
            ],
        ],
        colWidths=[9 * cm, 9 * cm],
    )

    bill_to_section.setStyle(
        TableStyle([
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ])
    )

    elements.append(bill_to_section)
    elements.append(Spacer(1, 30))

    # -------------------------
    # TABLE DATA
    # -------------------------

    data = [["No", "Product", "Qty", "Unit Price", "Total"]]

    subtotal = 0

    for i, item in enumerate(invoice.items.all(), start=1):
        total = item.quantity * item.product.price
        subtotal += total

        data.append([
            i,
            item.product.name,
            item.quantity,
            format_rupiah(item.product.price),
            format_rupiah(total),
        ])

    data.append(["", "", "", "TOTAL", format_rupiah(subtotal)])

    table = Table(
        data,
        colWidths=[2*cm, 8*cm, 2*cm, 2.5*cm, 3.5*cm]
    )

    # -------------------------
    # TABLE STYLE
    # -------------------------

    style = TableStyle([

        # Header
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_ORANGE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Font size
        ("FONTSIZE", (0, 0), (-1, -1), 12),

        # Alignment
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("ALIGN", (3, 1), (4, -1), "RIGHT"),

        # TOTAL row bold
        ("FONTNAME", (3, -1), (4, -1), "Helvetica-Bold"),

        # Padding
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ])

    # Alternating row colors
    for i in range(1, len(data) - 1):
        if i % 2 == 0:
            style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FAFAFA"))

    table.setStyle(style)

    elements.append(table)

    # -------------------------
    # BUILD PDF
    # -------------------------

    doc.build(elements, onFirstPage=draw_footer, onLaterPages=draw_footer)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{invoice.invoice_number}.pdf"'

    return response