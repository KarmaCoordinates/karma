import streamlit as st
import base64
from datetime import datetime, timezone, timedelta
import fpdf
from fpdf import FPDF
import dynamodb_functions as db
import journal_functions as jf
import pandas as pd

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

    columns_to_drop_from_report = [db.Columns().journal_entry, db.Columns().email, db.Columns().date, db.Columns().lives_to_moksha, db.Columns().score_ai_analysis_query, db.Columns().feedback, db.Columns().rating, db.Columns().percent_completed, db.Columns()._journal_entry]
    copy_dict = dict(data_dict)
    [copy_dict.pop(key, None) for key in columns_to_drop_from_report]    
    pdf = create_assessment_pdf(data_dict=copy_dict, score=score, analysis=analysis)
    pdf_output = pdf.output(dest='S')
    b64 = base64.b64encode(pdf_output).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="karma_coordinates_assessment.pdf">Assessment PDF</a>'
    st.markdown(href, unsafe_allow_html=True)


def create_journal_pdf(journal_df):
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
    pdf.cell(col_width, 10, txt=f'Karma Coordinates Journal created at {dt.strftime("%I:%M%p on %B %d, %Y")}', align='C')
    pdf.ln(10)
    
    pdf.cell(col_width, 10, txt="Your journal entries:", ln=True)
    df = journal_df[['date', 'journal_entry']].dropna(subset=['journal_entry'])
    df['entry_date'] = df['date'].astype(float).apply(datetime.fromtimestamp)
    # df['entry_date'] = pd.to_datetime(pd.to_numeric(df['date'], errors='coerce'), unit='s', )
    # df['entry_date'] = pd.to_datetime(df['date'], unit='s').dt.strftime('%m/%d/%y %H:%M') + ': ' + df['journal_entry']
    df['entry'] = df['entry_date'].dt.strftime('%m/%d/%y %H:%M') + ': ' + df['journal_entry']

    for e in df['entry']:
        pdf.multi_cell(w=col_width, txt=e, border=1, align='L', padding=2)
        pdf.ln(0.1)


    # for index, row in df.iterrows():
    #     pdf.multi_cell(w=col_width, txt=f'{row['entry_date'].strftime('%m/%d/%y %H:%M')}:{row['journal_entry']}', border=1, align='L', padding=2)
    #     pdf.ln(0.1)

        # pdf.multi_cell(col_width, 10, txt=f'{key} - {value}', border=1, align='L')
        # pdf.multi_cell(col_width, 10, txt=f'{key} - {value}'.encode('utf-8').decode('latin-1'), border=1, align='L')
        
    return pdf

def download_previous_month_journal():
    journal_df = jf.previous_month_journal_entries()

    if 'journal_entry' in journal_df:
        # st.subheader('''Download last month's journal as PDF''')
        # if st.button('Generate PDF Report'):
        # pdf_output = pdf.output(dest='S').encode('latin-1')
        # b64 = base64.b64encode(pdf_output).decode('latin-1')

        pdf = create_journal_pdf(journal_df)
        pdf_output = pdf.output(dest='S')
        b64 = base64.b64encode(pdf_output).decode('utf-8')
        href = f'''<a href="data:application/octet-stream;base64,{b64}" download="karma_coordinates_journal.pdf">Last month's journal</a>'''
        # st.markdown(href, unsafe_allow_html=True)
        return href

def download_current_month_journal():
    journal_df = jf.current_month_journal_entries()

    if 'journal_entry' in journal_df:
        # st.subheader('''Download current month's journal as PDF''')
        # if st.button('Generate PDF Report'):
        # pdf_output = pdf.output(dest='S').encode('latin-1')
        # b64 = base64.b64encode(pdf_output).decode('latin-1')

        pdf = create_journal_pdf(journal_df)
        pdf_output = pdf.output(dest='S')
        b64 = base64.b64encode(pdf_output).decode('utf-8')
        href = f'''<a href="data:application/octet-stream;base64,{b64}" download="karma_coordinates_journal.pdf">Current month's journal</a>'''
        # st.markdown(href, unsafe_allow_html=True)
        return href

def download_journal():
    href1 =  download_previous_month_journal()
    href2 = download_current_month_journal()    
    if href1:
        st.markdown(f'{href1} | {href2}', unsafe_allow_html=True)
    else:
        if href2:
            st.markdown(f'{href2}', unsafe_allow_html=True)




def main():
    pass

if __name__ == '__main__': main()
