import os
import uuid
from weasyprint import HTML, CSS

# Path to save the pdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "generated_proposals")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Basic Professional Styling
DEFAULT_CSS = CSS(string="""
    @page { size: A4; margin: 2.5cm; }
    body { font-family: 'Helvetica', 'Arial', sans-serif; font-size: 12pt; line-height: 1.6; color: #333; }
    h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-top: 0; }
    h2 { color: #2980b9; margin-top: 20px; }
    .header { text-align: right; font-size: 10pt; color: #7f8c8d; margin-bottom: 30px; }
    .footer { position: fixed; bottom: 0; right: 0; font-size: 10pt; color: #bdc3c7; }
    .price-box { background: #f8f9fa; border-left: 5px solid #27ae60; padding: 15px; margin: 20px 0; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
""")

def create_pdf(html_content:str, filename:str=None) -> str:
    """
    Converts an HTML string into a pdf file.
    Args: 
        html_content(str): The full HTML string of the proposal.
        filename(str): Optional filename. If None, a unique ID is generated.
        
    Returns:
        str: The absolute file path of the generated path
    """

    #1 Generate Filename

    if not filename:
        filename = f"proposal_{uuid.uuid4().hex[:8]}.pdf"

    if not filename.endswith(".pdf"):
        filename += ".pdf"

    file_path = os.path.join(OUTPUT_FOLDER,filename)
    print(f"Generating pdf: {filename}...")
    try:
        HTML(string=html_content).write_pdf(file_path, stylesheets=[DEFAULT_CSS])
        print(f"PDF saved at:{file_path}")
        return file_path
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None
    
#test block
# --- Test Block ---
if __name__ == "__main__":
    # Test HTML content
    test_html = """
    <div class="header">ProCode Bot | AI Generated Proposal</div>
    <h1>Project Proposal: Website Bot</h1>
    <p>Dear Client,</p>
    <p>Based on our analysis, here is the suggested implementation for your website bot.</p>
    
    <h2>Cost Estimate</h2>
    <div class="price-box">
        Total Estimated Cost: $12,500
    </div>
    
    <h2>Timeline</h2>
    <ul>
        <li>Phase 1: Discovery (1 Week)</li>
        <li>Phase 2: Development (4 Weeks)</li>
    </ul>
    """
    
    create_pdf(test_html, "test_proposal.pdf")