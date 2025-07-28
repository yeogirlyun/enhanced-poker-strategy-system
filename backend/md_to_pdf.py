# filename: md_to_pdf.py
"""
Markdown to PDF Converter Utility

A simple command-line tool to convert any Markdown file into a styled PDF document.
This utility uses the WeasyPrint library for high-quality rendering.

Usage:
    python3 md_to_pdf.py <input_filename.md>

Example:
    python3 md_to_pdf.py documentation.md
    This will create a 'documentation.pdf' file in the same directory.
"""
import sys
import os

try:
    import markdown
    from weasyprint import HTML, CSS
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

def convert_md_to_pdf(input_filename):
    """
    Reads a Markdown file, converts it to styled HTML, and saves it as a PDF.
    """
    # 1. Validate input file
    if not input_filename.endswith('.md'):
        print(f"❌ Error: Input file must have a '.md' extension.")
        return

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found at '{input_filename}'")
        return

    # 2. Define output filename
    base_name = os.path.splitext(input_filename)[0]
    pdf_filename = base_name + '.pdf'

    # 3. Define CSS for styling the PDF
    # This CSS is generic and suitable for most documents.
    css_string = """
        @page {
            size: A4; /* Default to portrait, can be changed if needed */
            margin: 2cm;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.6;
            font-size: 11pt;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
            line-height: 1.2;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        code {
            background-color: #ecf0f1;
            padding: 2px 4px;
            border-radius: 4px;
            color: #c0392b;
            font-family: monospace;
        }
        pre {
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 4px;
            white-space: pre-wrap;
        }
    """

    # 4. Perform the conversion
    html_string = markdown.markdown(md_content, extensions=['markdown.extensions.tables'])
    
    try:
        html = HTML(string=html_string)
        css = CSS(string=css_string)
        html.write_pdf(pdf_filename, stylesheets=[css])
        print(f"✅ Successfully converted '{input_filename}' to '{pdf_filename}'")
    except Exception as e:
        print(f"\n❌ PDF generation failed. (Error: {e})")

def main():
    """
    Main function to handle command-line arguments.
    """
    if not PDF_ENABLED:
        print("⚠️ PDF conversion is disabled.")
        print("   Please run 'pip install weasyprint markdown' to enable it.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python3 md_to_pdf.py <input_filename.md>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    convert_md_to_pdf(input_file)

if __name__ == '__main__':
    main()
