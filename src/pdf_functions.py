import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime, timezone, timedelta

# Option to download the result as PDF
def create_pdf(input_data, prediction):
    pdf = FPDF()
    # pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    # pdf.set_font('DejaVu', '', 14)

    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    dt = datetime.now(timezone(timedelta(hours=-5), 'EST')).strftime("%I:%M%p on %B %d, %Y")

    pdf.cell(200, 10, txt=f'Karma Coordinates Prediction Report at {dt}', ln=False, align='C')
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Input Features:", ln=True)
    for key, value in input_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}".encode('utf-8').decode('latin-1'), ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Predicted Karma Coordinates Label: {prediction}", ln=True)
    
    return pdf

def download_pdf(pdf, user_input, prediction_label):
    st.subheader('Download Prediction as PDF')
    if st.button('Generate PDF Report'):
        pdf = create_pdf(user_input, prediction_label[0])
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode('latin-1')
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="prediction_report.pdf">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)
