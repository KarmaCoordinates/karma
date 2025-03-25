import math
import numpy as np
import __constants

def __calculate_siddhi_influence(y, y_min=0, y_max=22.5, x_min=0.01, x_max=0.02):
    """
    Calculates steepness based on siddhi. Steepness is used in calculating lives
    Calculate the corresponding x value for a given y using the exponential function.

    Parameters:
    y (float): The target y value for which we want to find x.
    y_min (float): The minimum y value.
    y_max (float): The maximum y value.
    x_min (float): The minimum x value.
    x_max (float): The maximum x value.

    Returns:
    float or None: Corresponding x value, or None if y is out of the valid range.
    """

    # Ensure y is within the valid range
    if y < y_min:
        y = y_min
    if y > y_max:
        y = y_max
        # print(f"y value {y} is out of bounds.")
        # return None

    # Define constants for the exponential function
    c3 = y_min  # Set vertical shift
    c2 = 500.0  # Adjust this value to change the steepness of the curve

    # Calculate c1 based on the maximum y value at x_max
    c1 = (y_max - c3) / np.exp(c2 * x_max)

    # Calculate x using the rearranged exponential function
    x_value = 0
    try:
        # if c1 == 0: c1 = c1 + np.finfo(float).eps
        # if c2 == 0: c2 = c2 + np.finfo(float).eps
        # print(f'c1={c1}, c2={c2}, y={y}, c3={c3}')
        
        with np.errstate(divide="ignore"):
            x_value = (1 / c2) * np.log((y - c3) / c1)
    except:
        print(f"Exception in calculation for c2={c2}, c1={c1}: {e}")
        x_value = 0

    # Ensure x is within the valid range
    if x_value < x_min:
        x_value = x_min
    if x_value > x_max:
        x_value = x_max
        # print(f"x value {x_value} is out of bounds.")
        # return None

    return x_value


def __calculate_lives(y, y_min, y_max, steepness):

    # Calculate c1 based on the maximum y value
    c1 = (y_max - y_min) / np.exp(steepness * 1)  # This is derived from y = c1 * e^(steepness * 1) + y_min

    """
    Function to find the value of x given a specific y based on the 
    equation: y = c1 * exp(steepness * x) + y_min.

    Parameters:
    y (float): The y-value for which we want to find the corresponding x-value.

    Returns:
    float: Corresponding x-value or None if it is out of range or invalid.
    """

    # y = c1 + y_min    
    # Check if y is within valid bounds
    if (y < y_min):
        y = y_min + 0.1

    if (y > c1 + y_min):
        y = c1 + y_min

    # if (y > y_max):
    #     y = y_max


    # Calculate x using the rearranged formula
    try:
        # Ensure argument to log is positive
        with np.errstate(divide="ignore"):
            x_value = (1 / steepness) * np.log((y - y_min) / c1)
        return x_value
    except Exception as e:    
        print(f"Error in calculation for steepness={steepness}, c1={c1}: {e}")
        return None

def calculate_karma_coordinates(category_scores, score_range):
    total_score = sum(category_scores.values())
    siddhi_score = category_scores.get(__constants.CATEGORY_SIDDHI)
    y_min = score_range['minimum_score']
    y_max = score_range['maximum_score']
    steepness_min=0.01
    steepness_max=0.02  
    siddhi_steepness = __calculate_siddhi_influence(y=siddhi_score, y_min=0, y_max=y_max, x_min=steepness_min, x_max=steepness_max, )
    remaining_lives = __calculate_lives(total_score, y_min=y_min, y_max=y_max, steepness=siddhi_steepness)
    return abs(round(remaining_lives))

    


def main():
    # category_scores = {'Viparyayah (विपर्यय)': -20220.0, 'Aśakti (अशक्ति)': -22.0, 'Tuṣṭi (तुष्टि)': -5.0, 'Siddhi (सिद्धि)': 206.0, 'Lifestyle': 1000.5}
    # score_range = {'minimum_score': -1480.0, 'maximum_score': 222.5, 'number_of_questions': 57}
    # print(calculate_karma_coordinates(category_scores=category_scores, score_range=score_range))
    pass

if __name__ == '__main__': main()
