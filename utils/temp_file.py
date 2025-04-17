import os

def save_uploaded_file_temporarily(uploaded_file,file_id):
    if not uploaded_file:
        return
    try:
        os.makedirs("temp_files", exist_ok=True)
        if '.' in uploaded_file.name:
            file_type = uploaded_file.name.split('.')[-1]
        else:
            file_type = ""
        filename = os.path.basename(f"{str(file_id)}.{file_type}")
        destination_path = os.path.join("temp_files", filename)

        with open(destination_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return destination_path
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return