import os

from django.conf import settings
from django.shortcuts import render

from .services import split_csv, pack_to_zip, convert_chunk_files_to_xlsx, convert_chunk_files_to_mysql, send_mail

def index(request):
    output_directory = 'output_directory'

    context = {
        'message': ""
    }

    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        rows_per_file = request.POST["rows-per-file"]
        output_ext = request.POST["output-extension"]
        table_name = request.POST["table-name"]
        recipient_email = request.POST["email"]
        sender_email = settings.EMAIL_SENDER
        sender_password = settings.EMAIL_PASSWORD

        output_zip_path = 'output.zip'
        # Split CSV
        if rows_per_file == "":
            rows_per_file = float('inf')
        else:
            rows_per_file = int(rows_per_file)
            
        split_csv(csv_file, output_directory, rows_per_file)
        
        if output_ext == "xlsx":
            convert_chunk_files_to_xlsx(output_directory)
        elif output_ext == "sql":
            convert_chunk_files_to_mysql(output_directory, table_name)
        
        # Create a zip file containing the split CSV files
        response = pack_to_zip(output_directory, output_zip_path)

        if recipient_email:
            try:
                send_mail("Zedytowany plik CSV", "Plik został zedytowany według twoich wymagań i jest dostępny do pobrania w załączniku.", recipient_email, sender_email, sender_password, output_zip_path)

            except:
                context["message"] = "Email nie został wysłany. Wystąpił błąd."
            else:
                context['message'] = "Email z plikiem został wysłany."            

            # request.POST = 
            response = render(request, 'csv_app/index.html', context)

        for root, dirs, files in os.walk(output_directory):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
        
        os.remove(output_zip_path)    
            
        return response

    return render(request, 'csv_app/index.html', context)

