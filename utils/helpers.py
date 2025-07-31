def km_driven_cleaner(value):
    """
    Converts a string representing kilometers driven into an integer value.

    The input is expected to be a string that may end with:
    - 'L' representing 'Lakh' (1 Lakh = 100,000)
    - 'k' representing 'Thousand' (1k = 1,000)

    The function parses the numeric part of the string, converts it to a float and then multiplies it accordingly:
    - If the value ends with 'L', it multiplies the number by 1,00,000.
    - If the value ends with 'k', it multiplies the number by 1,000.

    Parameters:
        value (str): A string indicating the kilometers driven, using 'k' or 'L' notation.

    Returns:
        km_driven (int): The equivalent number of kilometers as an integer.

    Example:
        >>> km_driven_cleaner("1.5L")
        150000
        >>> km_driven_cleaner("12k")
        12000
    """
    if value.strip().endswith('L'):
        return round(float(value.replace('L',''))*100000)
    else:
        return round(float(value.replace('k',''))*1000)