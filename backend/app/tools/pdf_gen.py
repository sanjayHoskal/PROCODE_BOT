import os
import uuid
from weasyprint import HTML, CSS

# Path to save the pdf
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "generated_proposals")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- UPDATED CSS ---
DEFAULT_CSS = CSS(string="""
    @page { 
        size: A4; 
        margin: 2cm; 
        @bottom-center { content: element(footer); } /* Standard print footer */
    }
    
    body { 
        font-family: 'Helvetica', 'Arial', sans-serif; 
        font-size: 11pt; 
        line-height: 1.5; 
        color: #333;
    }

    /* Logo Positioning */
    .header-container {
        display: block;
        height: 80px;
        margin-bottom: 20px;
        border-bottom: 2px solid #2c3e50;
    }
    .logo {
        float: right;
        height: 60px; /* Adjust size */
        width: auto;
    }
    .company-name {
        float: left;
        font-size: 20pt;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 15px;
    }

    /* Content Styling */
    h1 { color: #2c3e50; margin-top: 20px; }
    h2 { color: #2980b9; margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    
    .price-box { 
        background: #f8f9fa; 
        border-left: 5px solid #27ae60; 
        padding: 15px; 
        margin: 20px 0; 
        font-weight: bold;
        font-size: 1.2em;
    }

    /* Footer Styling */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 50px;
        text-align: center;
        font-size: 9pt;
        color: #7f8c8d;
        border-top: 1px solid #ddd;
        padding-top: 10px;
    }
""")

def create_pdf(html_content:str, filename:str=None) -> str:
    if not filename:
        filename = f"proposal_{uuid.uuid4().hex[:8]}.pdf"
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    file_path = os.path.join(OUTPUT_FOLDER,filename)
    print(f"Generating pdf: {filename}...")
    try:
        # base_url is needed if you use local images
        HTML(string=html_content, base_url=BASE_DIR).write_pdf(file_path, stylesheets=[DEFAULT_CSS])
        print(f"PDF saved at: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None