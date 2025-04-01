import csv
import os
import zipfile
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email import encoders
from email.mime.base import MIMEBase

def split_csv(csv_file, output_directory, rows_per_file):
    os.makedirs(output_directory, exist_ok=True)

    csv_content = csv_file.read().decode('utf-8').splitlines()
 
    reader = csv.reader(csv_content)
    header = next(reader)

    current_chunk = 1
    current_file = None
    current_rows = []

    for row in reader:
        current_rows.append(row)

        if len(current_rows) == rows_per_file:
            current_file = os.path.join(output_directory, f'chunk_{current_chunk}.csv')
            with open(current_file, 'w', newline='') as output_file:
                writer = csv.writer(output_file)
                writer.writerow(header)
                writer.writerows(current_rows)

            current_chunk += 1
            current_rows = []

    if current_rows:
        current_file = os.path.join(output_directory, f'chunk_{current_chunk}.csv')
        with open(current_file, 'w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header)
            writer.writerows(current_rows)


def pack_to_zip(output_directory, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(output_directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_directory))

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=output.zip'

    with open(zip_file_path, 'rb') as zip_file:
        response.write(zip_file.read())
    
            
    return response

def convert_chunk_files_to_xlsx(output_directory):

    for root, dirs, files in os.walk(output_directory):
        for file in files:  
            csv_file_path = os.path.join(root, file)

            with open(csv_file_path, 'r') as csv_file:
                excel_file = convert_csv_to_xlsx(csv_file)
            
            xlsx_file_path = os.path.join(root, f'{os.path.splitext(file)[0]}.xlsx')
            with open(xlsx_file_path, 'wb') as xlsx_file:
                xlsx_file.write(excel_file.getvalue())
                
            os.remove(csv_file_path)


def convert_csv_to_xlsx(csv_file):

    df = pd.read_csv(csv_file)

    excel_file = BytesIO()

    df.to_excel(excel_file, engine='openpyxl', index=False)

    return excel_file

                
def convert_csv_to_mysql_code(csv_file, table_name):
    df = pd.read_csv(csv_file)

    for col in df.columns:
        df[col] = df[col].replace('"', '')

    columns_definition = ', '.join([f"`{col}` VARCHAR(255)" for col in df.columns])
    create_table_code = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition});"

    columns = ', '.join([f"`{col}`" for col in df.columns])
    
    # Generate values for all rows
    values_list = []
    for index, row in df.iterrows():
        values = ', '.join(["'%s'" % value for value in row])
        values_list.append(f"({values})")

    import_code = f"INSERT INTO {table_name} ({columns}) VALUES {', '.join(values_list)};"

    result = (create_table_code + '\n\n' + import_code)
    
    return result



def convert_chunk_files_to_mysql(output_directory, table_name):

    for root, dirs, files in os.walk(output_directory):
        for file in files:
            
            csv_file_path = os.path.join(root, file)

            # Convert CSV to MYSQL using the existing function
            with open(csv_file_path, 'r') as csv_file:
                mysql_code = convert_csv_to_mysql_code(csv_file, table_name)
            
            # Save SQL file, overwriting the existing CSV file
            sql_file_path = os.path.join(root, f'{os.path.splitext(file)[0]}.sql')
            with open(sql_file_path, 'wb') as sql_file:
                sql_file.write(mysql_code.encode('utf-8'))
                
            # Remove old CSV file
            os.remove(csv_file_path)


    

def send_mail(subject, body, recipient_email, sender, password, attachment_path=None):

    # Create the message
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient_email

    # Attach the body of the email
    html_part = MIMEText(body, 'plain')
    message.attach(html_part)

    # Attach the attachment if provided
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {attachment_path}")
        message.attach(part)

    # Connect to the SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient_email, message.as_string())
