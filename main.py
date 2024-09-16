import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from jinja2 import Template, TemplateError
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
import os

# Set up Google Sheets API client
scope = ['https://www.googleapis.com/auth/spreadsheets.readonly',
         'https://www.googleapis.com/auth/drive.readonly']

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'optical-fin-304512-f3f98dcddc4a.json', scope)
    client = gspread.authorize(creds)
except Exception as e:
    exit(1)

# Open the Google Sheet
try:
    sheet = client.open_by_url(
        'https://docs.google.com/spreadsheets/d/1H1ZmSxkaiRzdeFgTStme5hawLoRfbP3Ac2g2gYRK3X0/edit?gid=0#gid=0').sheet1
    data = sheet.get_all_records()
except Exception as e:
    exit(1)

# Convert the data to a DataFrame
try:
    df = pd.DataFrame(data)
except Exception as e:
    exit(1)

# Load your HTML template
try:
    with open('template.html', 'r') as file:
        html_template = file.read()
except FileNotFoundError as e:
    exit(1)
except IOError as e:
    exit(1)

# Define the path to wkhtmltopdf executable
# Update this path based on your installation
path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# Configure pdfkit with the path to wkhtmltopdf
try:
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
except Exception as e:
    exit(1)

# Define a function to convert HTML to PDF
def convert_html_to_pdf(html_content, index):
    pdf_filename = f"time_blocking_{index + 1}.pdf"
    try:
        pdfkit.from_string(html_content, pdf_filename, configuration=config)
    except Exception as e:
        return None
    return pdf_filename

# List to keep track of generated PDF filenames
pdf_files = []

# Process each row and generate a PDF
for index, row in df.iterrows():
    template = Template(html_template)
    html_content = template.render(
        formatted_date=row.get('formattedDate', ''),
        wake_time=row.get('wakeTime', ''),
        mantra=row.get('mantra', ''),
        memo=row.get('memo', ''),
        reflection=row.get('reflection', ''),
        priorities=row.get('priorities', ''),
        todos=row.get('todos', ''),
        time_blocks=row.get('timeBlocks', '')
    )

    pdf_filename = convert_html_to_pdf(html_content, index)
    if pdf_filename:
        pdf_files.append(pdf_filename)

# Merge PDFs into one
output_filename = 'merged_time_blocking_pdfs.pdf'
pdf_writer = PdfWriter()

for pdf_file in pdf_files:
    try:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])
    except Exception as e:
        pass

# Write the merged PDF to a file
try:
    with open(output_filename, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
except IOError as e:
    pass

# Optionally, clean up individual PDF files
for pdf_file in pdf_files:
    try:
        os.remove(pdf_file)
    except Exception as e:
        pass
