import markdown
import s3_functions as s3f
import os

def md_to_html(static_files_folder, md_filename, html_filename):
    bucket_name = 'karmacoordinates'
    object_key = html_filename

    md_filename_path = f'{static_files_folder}/{md_filename}'
    html_filename_path = f'{static_files_folder}/{html_filename}'

    markdown.markdownFromFile(input=md_filename_path, output=html_filename_path, encoding="utf-8")

    with open(html_filename_path, 'r') as original:
        data = original.read()
    with open(html_filename_path, 'w') as modified:
        modified.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8">\n' + data)    

    s3f.save_html_to_s3(html_filename_path, bucket_name, object_key)

    os.remove(html_filename_path)


md_to_html('.static', 'calculating_karma_coordinates.md', 'calculating_karma_coordinates.html')