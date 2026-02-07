import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

st.set_page_config(
    page_title="PDF Cover & Watermark Tool",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Header ----------
st.markdown(
    """
    <h1 style="text-align:center;">📄 PDF Cover & Watermark Tool</h1>
    <p style="text-align:center; color:#6c757d;">
    Add front & back covers and a logo watermark professionally
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ---------- Upload Cards ----------
st.markdown("### 1️⃣ Upload Files")

with st.container(border=True):
    st.subheader("Main PDF")
    main_pdf = st.file_uploader("Upload main document", type=["pdf"])

with st.container(border=True):
    st.subheader("Front Cover PDF")
    front_cover_pdf = st.file_uploader("Upload front cover", type=["pdf"])

with st.container(border=True):
    st.subheader("Back Cover PDF")
    back_cover_pdf = st.file_uploader("Upload back cover", type=["pdf"])

with st.container(border=True):
    st.subheader("Logo Image")
    logo_file = st.file_uploader("Upload logo (PNG / JPG)", type=["png", "jpg", "jpeg"])

# ---------- Output Settings ----------
with st.container(border=True):
    st.subheader("2️⃣ Output Settings")
    output_name = st.text_input(
        "Output file name",
        placeholder="example: final_report"
    )
    st.caption("`.pdf` will be added automatically")

st.divider()

# ---------- PDF Logic ----------
def create_watermark(page_width, page_height, logo_img):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFillAlpha(0.1)  # 10% opacity

    logo_width = page_width * 0.3
    ratio = logo_img.height / logo_img.width
    logo_height = logo_width * ratio

    x = (page_width - logo_width) / 2
    y = (page_height - logo_height) / 2

    c.drawImage(
        ImageReader(logo_img),
        x, y,
        width=logo_width,
        height=logo_height,
        mask="auto"
    )

    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def add_watermark(page, logo_img):
    watermark = create_watermark(
        float(page.mediabox.width),
        float(page.mediabox.height),
        logo_img
    )
    page.merge_page(watermark)
    return page


# ---------- Action ----------
ready = all([
    main_pdf,
    front_cover_pdf,
    back_cover_pdf,
    logo_file,
    output_name.strip()
])

if st.button(
    "🚀 Generate PDF",
    use_container_width=True,
    disabled=not ready
):
    with st.spinner("Processing PDF…"):
        writer = PdfWriter()
        logo_image = Image.open(logo_file)

        # Front cover (no watermark)
        for page in PdfReader(front_cover_pdf).pages:
            writer.add_page(page)

        # Main PDF (with watermark)
        for page in PdfReader(main_pdf).pages:
            writer.add_page(add_watermark(page, logo_image))

        # Back cover (no watermark)
        for page in PdfReader(back_cover_pdf).pages:
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

    st.success("✅ PDF generated successfully")

    st.download_button(
        "⬇️ Download PDF",
        data=output,
        file_name=f"{output_name}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ---------- Footer ----------
st.markdown(
    """
    <hr>
    <p style="text-align:center; font-size:0.85rem; color:#6c757d;">
    Secure · No files stored · Built with Streamlit
    </p>
    """,
    unsafe_allow_html=True
)
