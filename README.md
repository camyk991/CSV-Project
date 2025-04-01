# CSV Splitter & Converter

A tool for splitting large CSV files into smaller chunks, converting to different formats, and exporting to SQL. Compatible only with Python 3.8.

**Tech Stack:**
- Python 3.8
- Django 3.2+ (or your specific version)
- Pandas (for data manipulation)
- Openpyxl (for Excel conversion)

##  Features
- Split CSV files into smaller parts
- Convert to multiple formats:
  - CSV (keep original format)
  - XLSX (Excel)
  - SQL (database import)
- Optional email delivery
- Simple web interface


### Prerequisites
- Python 3.8 

### Setup instructions:
   ```bash
   pip install -r requirements.txt
   pip manage.py runserver