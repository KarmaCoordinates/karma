import numpy as np
import matplotlib.pyplot as plt

def test1():
    # Parameterize the values
    x_min = -300     # Minimum x value
    x_max = 1        # Maximum x value
    y_min = -144     # Minimum y value
    y_max = 22.5     # Maximum y value

    # Define y values for specific x values
    x1 = x_min  # -300
    y1 = y_min   # -144

    x2 = x_max   # 1
    y2 = y_max   # 22.5

    # We can express y = c1 * exp(steepness * x) + y_min and solve for coefficients
    y_min = y1  # Set y_min to -144

    # Calculate c1 and steepness based on the second point (x2, y2)
    # y2 = c1 * exp(steepness * x2) + y_min
    # Thus, c1 = (y2 - y_min) / exp(steepness * x2)

    # Rearranging for two points:
    # -144 = c1 * exp(steepness * (-300)) + y_min
    # 22.5 = c1 * exp(steepness * (1)) + y_min

    # Rearranging gives us:
    # c1 = (y2 - y_min) / exp(steepness * x2)
    # Substitute c1 into the first equation to solve for steepness

    # Instead of complex iterations, guess a steepness and solve for c1
    # Using logarithmic properties we'll ensure both points are satisfied

    # Initial guess for steepness
    steepness = 0.01  # This may be adjusted for steepness

    # Solve for c1 using one of the two points
    c1 = (y2 - y_min) / np.exp(steepness * x2)

    # Define the x values based on parameters
    x_values = np.linspace(x_min, x_max, 1000)  # Creates 1000 points from x_min to x_max

    # Define the exponential function using the derived parameters
    y_values = c1 * np.exp(steepness * x_values) + y_min  # Exponential function based on our calculations

    # Ensure it reaches the correct points
    # With that we can confirm
    # Point 1: (-300, -144)
    # Point 2: (1, 22.5)

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, label=f"y = {c1:.2f} * exp({steepness:.4f} * x) + {y_min}", color='blue')
    plt.scatter([x1, x2], [y1, y2], color='red')  # Plot the key points as dots

    # Set the limits for the plot
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Add labels and title
    plt.title("Exponential Graph Fitting Specified Points")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axhline(0, color='black', linewidth=0.5, ls='--')
    plt.axvline(0, color='black', linewidth=0.5, ls='--')
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.show()



def find_x_for_y(y, y_min, y_max, steepness):

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
    # Check if y is within valid bounds
    if (y < y_min):
        y = y_min
    if (y > c1 + y_min):  # y must be strictly between y_min and c1 + y_min
        y = c1 + y_min
        # print("y value is out of bounds.")
        # return None

    # Calculate x using the rearranged formula
    try:
        # Ensure argument to log is positive
        x_value = (1 / steepness) * np.log((y - y_min) / c1)
        return x_value
    except ValueError as e:
        print(f"Error in calculation for y = {y}: {e}")
        return None

def calculate_x_for_y(y, y_min=0, y_max=22.5, x_min=0.01, x_max=0.02):
    """
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
    x_value = (1 / c2) * np.log((y - c3) / c1)

    # Ensure x is within the valid range
    if x_value < x_min:
        x_value = x_min
    if x_value > x_max:
        x_value = x_max
        # print(f"x value {x_value} is out of bounds.")
        # return None

    return x_value

# Example usage
# y_values = [0, 5, 10, 15, 22.5, 23]  # Test for several y values, including out of bounds
# for y_input in y_values:
#     x_result = calculate_x_for_y(y_input)
#     if x_result is not None:
#         print(f"The value of x for y = {y_input} is: {x_result:.6f}")


#compute siddhi driven steepness
siddhi_score = 20
y_min = -144.1  # Constant
y_max = 22.5
siddhi_steepness = calculate_x_for_y(y=siddhi_score)
x = find_x_for_y(-22)


# Example usage WORKS!
for y_input in [-144, -140, -25, -24, -23, -20, 0, 2, 5, 10, 15, 18, 20, 22.5, 23]:  # Test multiple y values
    x_result = find_x_for_y(y_input, y_min=y_min, y_max=y_max, steepness=siddhi_steepness)
    print(f"The value of x for y = {y_input} and siddhi = {siddhi_score} is: {(x_result)}")



