import markdown

def md_to_html(static_files_folder, md_filename, html_filename):
    markdown.markdownFromFile(input=f'{static_files_folder}/{md_filename}', output=f'{static_files_folder}/{html_filename}', encoding="utf-8")

md_to_html('.static', 'calculating_karma_coordinates.md', 'calculating_karma_coordinates.html')