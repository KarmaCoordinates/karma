import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime, timezone, timedelta

# Option to download the result as PDF
def create_pdf(data, prediction):
    pdf = FPDF()
    # pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    # pdf.set_font('DejaVu', '', 14)

    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # pdf.set_section_title_styles("font","helvetica","",10,"0,0,255");


    # # pdf.set_font("Times", size=10)
    # line_height = pdf.font_size * 2.5
    # # col_width = pdf.epw / 4.5
    # col_width = 150

    # lh_list = [] #list with proper line_height for each row
    # use_default_height = 0 #flag

    # #create lh_list of line_heights which size is equal to num rows of data
    # for row in data:
    #     for datum in row:
    #         word_list = datum.split()
    #         number_of_words = len(word_list) #how many words
    #         if number_of_words>2: #names and cities formed by 2 words like Los Angeles are ok)
    #             use_default_height = 1
    #             new_line_height = pdf.font_size * (number_of_words/2) #new height change according to data 
    #     if not use_default_height:
    #         lh_list.append(line_height)
    #     else:
    #         lh_list.append(new_line_height)
    #         use_default_height = 0

    # #create your fpdf table ..passing also max_line_height!
    # for j,row in enumerate(data):
    #     for datum in row:
    #         line_height = lh_list[j] #choose right height for current row
    #         pdf.multi_cell(col_width, line_height, f"{datum}".encode('utf-8').decode('latin-1'), border=1,align='L') #,ln=3, max_line_height=pdf.font_size)
    #     pdf.ln(line_height)

# pdf.output('table_with_cells.pdf')

    
    dt = datetime.now(timezone(timedelta(hours=-5), 'EST')).strftime("%I:%M%p on %B %d, %Y")
    # pdf.set_creation_date(dt)
    pdf.set_author('KarmaCoordinates.org')
    # pdf.table(col_widths=2,markdown=True)
    
    col_width = 185
    pdf.cell(col_width, 10, txt=f'Karma Coordinates Prediction Report at {dt}', align='C')
    pdf.ln(10)
    
    pdf.cell(col_width, 10, txt="Your inputs:", ln=True)
    for key, value in data.items():
        pdf.multi_cell(col_width, 10, txt=f'{key} - {value}'.encode('utf-8').decode('latin-1'), border=1, align='L')
    
    pdf.ln(10)
    pdf.cell(col_width, 10, txt="Your Karma Coordinates:", ln=True)
    pdf.multi_cell(col_width, 10, txt=f"{prediction}".encode('utf-8').decode('latin-1'), border=1, align='L')
    
    return pdf

def download_pdf(pdf):
    st.subheader('Download Prediction as PDF')
    if st.button('Generate PDF Report'):
        # pdf = create_pdf(user_input, prediction_label[0])
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode('latin-1')
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="prediction_report.pdf">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)
