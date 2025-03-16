import re
import pandas as pd
import numpy as np
from urllib import request
import datetime
import calendar
import json
from decimal import Decimal
import time

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def internet_on():
    try:
        request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except request.URLError as err: 
        return False
    
def hard_wrap_string_vectorized(s, width):
    """Wrap a string into lines with a maximum width and returns a single string with <br> for line breaks."""
    if not s:
        return
    
    words = str(s).split()  # Split the string into words
    if not words:      # Return an empty string if input is empty
        return ""

    # Initialize the string accumulator
    wrapped_lines = []
    current_line = []

    # Use numpy for efficient word length calculation
    word_lengths = np.array([len(word) for word in words])

    for i in range(len(words)):
        # Check if current line plus this word exceeds the width
        if len(current_line) + (1 if current_line else 0) + word_lengths[i] > width:
            wrapped_lines.append(' '.join(current_line))
            wrapped_lines.append("<br>")
            current_line = [words[i]]  # Start a new line with this word
        else:
            current_line.append(words[i])

    # Append any remaining words
    if current_line:
        wrapped_lines.append(' '.join(current_line))

    return ''.join(wrapped_lines)


def insert_line_breaks(text, max_length=50):
    if not text:
        return
    
    words = str(text).split()  # Split the text into words
    result = []  # Initialize the result list
    current_line = ""  # Initialize an empty line

    for word in words:
        # Check if adding the next word would exceed the max_length
        if len(current_line) + len(word) + 1 > max_length:
            # If it does exceed, append current line to result and reset
            result.append(current_line.strip())
            current_line = word + " "  # Start a new line with the current word
        else:
            current_line += word + " "  # Add word to the current line

    # Don't forget to add the last line
    if current_line:
        result.append(current_line.strip())

    # Join the lines with <BR> tags
    return "<BR>".join(result)

# # Example DataFrame with a text column
# data = {
#     'text_column': [
#         "This is a very long string that needs to be wrapped in a specific width for display purposes.",
#         "Another long string that should also be wrapped at a specific width.",
#         "Short one to see the different lengths."
#     ]
# }

# df = pd.DataFrame(data)

# # Apply the hard wrap function to the 'text_column'
# width = 40
# df['wrapped_text'] = df['text_column'].apply(lambda x: hard_wrap_string_vectorized(x, width))

# # Print the resulting DataFrame
# print(df[['text_column', 'wrapped_text']])


def is_valid_email(email):
    # """Check if the email is a valid format."""
    # Regular expression for validating an Email
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    # If the string matches the regex, it is a valid email
    if re.match(regex, email):
        return True
    else:
        return False


def previous_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    return last_month.strftime("%Y%m")


def get_start_end_month(input_yyyymm):
    input_ = str(input_yyyymm)
    year = int(input_[:4])
    month = int(input_[4:])
    start = int(input_+"01")
    end = int(input_+str(calendar.monthrange(year, month)[1]))

    return start, end

def previous_month_timestamp():
    start, end = get_start_end_month(previous_month())
    start_timestamp = datetime.datetime.strptime(str(start), "%Y%m%d").timestamp()
    end_timestamp = datetime.datetime.strptime(str(end), "%Y%m%d").timestamp()
    return start_timestamp, end_timestamp


def current_month():
    today = datetime.date.today()
    return today.strftime("%Y%m")

def current_month_timestamp():
    start, end = get_start_end_month(current_month())
    start_timestamp = datetime.datetime.strptime(str(start), "%Y%m%d").timestamp()
    end_timestamp = datetime.datetime.strptime(str(end), "%Y%m%d").timestamp()
    return start_timestamp, end_timestamp


def unix_epoc(months_ago=1):
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=months_ago*30) #Approximating a month as 30 days
    datetime_six_months_ago = datetime.datetime(six_months_ago.year, six_months_ago.month, six_months_ago.day, 0, 0, 0)
    timestamp_six_months_ago = int(time.mktime(datetime_six_months_ago.timetuple()))
    return timestamp_six_months_ago


def main():
    pass

if __name__ == '__main__': main()

