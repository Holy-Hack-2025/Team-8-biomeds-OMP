#Write a function that calculates a number and multiplies it by 2
# and then adds 3 to the result. The function should take one argument,
# which is the number to be multiplied and added to.
def calculate_and_modify(number):
    """
    This function takes a number, multiplies it by 2, and then adds 3 to the result.

    Args:
    number (int or float): The number to be modified.

    Returns:
    int or float: The modified result.
    """
    result = (number * 2) + 3
    return result

print(calculate_and_modify(5))