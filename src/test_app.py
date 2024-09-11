import streamlit as st

percent_completed = 58.009
lives_to_moksha = 24

ref = '\\allowbreak\\tiny\\text{{(Sandeep Dixit, 2024. \\textit{{Calculating Karma Coordinates}})}}'
completed = f'\\allowbreak\\small\\text{{based on {round(percent_completed)}\\% completion.}}'
score = f'\\large\\text{{Number of lives to Moksha:}}\\huge{{ {lives_to_moksha} }}'
result = f':orange-background[$${score} {completed}$$] $${ref}$$'

st.markdown(result)