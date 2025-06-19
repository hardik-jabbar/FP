import markdown
from weasyprint import HTML, CSS
import os
from datetime import datetime

def convert_markdown_to_pdf():
    try:
        # Read the markdown file
        with open('API_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'codehilite']
        )

        # Create a simple HTML document
        html_string = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>FarmPower API Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                code {{ background: #f8f9fa; padding: 2px 4px; }}
                pre {{ background: #f8f9fa; padding: 15px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
            </style>
        </head>
        <body>
            <h1>FarmPower API Documentation</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            {html_content}
        </body>
        </html>
        """

        # Create PDF directly from HTML string
        HTML(string=html_string).write_pdf('FarmPower_API_Documentation.pdf')
        print("PDF generated successfully!")

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Print more detailed error information
        import traceback
        print("\nDetailed error:")
        print(traceback.format_exc())

if __name__ == '__main__':
    convert_markdown_to_pdf() 
