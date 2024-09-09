import streamlit as st
import base64
from datetime import datetime, timezone, timedelta
import fpdf
from fpdf import FPDF
import dynamodb_functions as db

def create_assessment_pdf(data_dict, score, analysis):
    pdf = FPDF()

    # pdf.add_blank_page(width=250, height=700)
    pdf.add_page()
    # pdf.set_font("Arial", size=12)
    # pdf.add_font(family='gargi', fname='.static/gargi.ttf', uni=True)
    # pdf.add_font(family='Devanagari', fname='.static/Devanagari.ttf', uni=True)
    pdf.add_font(family='Arial Unicode MS', fname='.static/arialuni.ttf', uni=True)
    pdf.set_font("Arial Unicode MS", size=12)
    # pdf.add_font(family='DejaVu', fname='.static/DejaVuSansCondensed.ttf', uni=True)
    # pdf.set_font("DejaVu", size=12)
    # pdf.add_font(family='NotoSans', fname='.static/NotoSansDevanagari-Regular.ttf', uni=True)
    # pdf.set_font("NotoSans", size=12)


    dt = datetime.now(timezone(timedelta(hours=-5), 'EST')) #.strftime("%I:%M%p on %B %d, %Y")
    # pdf.set_creation_date(dt)
    pdf.set_author('KarmaCoordinates.org')
    
    col_width = 185
    pdf.cell(col_width, 10, txt=f'Karma Coordinates Assessment Report at {dt.strftime("%I:%M%p on %B %d, %Y")}', align='C')
    pdf.ln(10)
    
    pdf.cell(col_width, 10, txt="Your inputs:", ln=True)
    for key, value in data_dict.items():
        pdf.multi_cell(w=col_width, txt=f'{key} - {value}', border=1, align='L', padding=2)
        pdf.ln(0.1)

        # pdf.multi_cell(col_width, 10, txt=f'{key} - {value}', border=1, align='L')
        # pdf.multi_cell(col_width, 10, txt=f'{key} - {value}'.encode('utf-8').decode('latin-1'), border=1, align='L')
    
    if score:
        pdf.ln(10)
        pdf.cell(col_width, 10, txt="Your Karma Coordinates:", ln=True)
        # pdf.multi_cell(col_width, 10, txt=f"{prediction}".encode('utf-8').decode('latin-1'), border=1, align='L')
        pdf.multi_cell(col_width, 10, txt=f"{score}", border=1, align='L', )

    if analysis:
        pdf.ln(10)
        pdf.cell(col_width, txt=f"AI analysis:", ln=True)
        pdf.multi_cell(col_width, 10, txt=f"{analysis}", border=1, align='L', )
    
    return pdf

def download_assessment_pdf(data_dict, score, analysis=None):
    st.subheader('Download Assessment as PDF')
    # if st.button('Generate PDF Report'):
    # pdf_output = pdf.output(dest='S').encode('latin-1')
    # b64 = base64.b64encode(pdf_output).decode('latin-1')

    columns_to_drop_from_report = [db.Columns().journal_entry, db.Columns().email, db.Columns().date, db.Columns().lives_to_moksha, db.Columns().score_ai_analysis_query, db.Columns().feedback, db.Columns().rating]
    copy_dict = dict(data_dict)
    [copy_dict.pop(key, None) for key in columns_to_drop_from_report]    
    pdf = create_assessment_pdf(data_dict=copy_dict, score=score, analysis=analysis)
    pdf_output = pdf.output(dest='S')
    b64 = base64.b64encode(pdf_output).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="karma_coordinates_assessment.pdf">Assessment PDF</a>'
    st.markdown(href, unsafe_allow_html=True)


def main():
    pass

if __name__ == '__main__': main()
