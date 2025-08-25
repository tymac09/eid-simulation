from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_name: str, context: dict):
    """
    Renders a Django template to PDF bytes using xhtml2pdf.
    Returns (pdf_bytes, error) where error is None if success.
    """
    html = get_template(template_name).render(context)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result)
    if pisa_status.err:
        return None, "PDF generation error"
    return result.getvalue(), None
