import pandas as pd


def reverse_dict(dictionary):
    """Reverse a dictionary.

    Keys become values and vice versa.

    Parameters
    ----------
    dictionary : dict
        Dictionary to reverse

    Returns
    -------
    dict
        Reversed dictionary

    Raises
    ------
    TypeError
        If there is a value which is unhashable, therefore cannot be a dictionary key.
    """
    return {i: value for value, i in dictionary.items()}


def encode_label(dataframe, column, column_encoded, encoding_dictionary=None):
    """Encode ``column`` label in ``dataframe`` with ``encoding_dictionary`` provided.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The DataFrame to read and to write to.
    column : str
        Name of the column to encode
    column_encoded : str
        Name of the encoded column, which will be added to ``dataframe``.
    encoding_dictionary : dict, optional
        Dictionary used to encode values, where the keys are the original values and the
        values are the encoded values. If None (which is the default) each categorical
        value will be mapped to an integer (0 to n_values - 1).

    Returns
    -------
    pandas.DataFrame
        A copy of ``dataframe`` with the new column ``column_encoded``.

    dict
        Encoding dict reversed

    Raises
    ------
    ValueError
        If the column ``column`` does not exist in ``dataframe``.
    ValueError
        If the ``encoding_dict`` is missing some values to encode (keys).
    """

    if column not in dataframe.columns:
        raise ValueError(f"Column {column} does not exist in dataframe")

    if encoding_dictionary:
        values_to_encode = set(dataframe[column].unique())

        if values_to_encode > set(encoding_dictionary.keys()):
            missing_values = values_to_encode - set(encoding_dictionary.keys())
            raise ValueError(
                "Encoding dictionary is missing some keys: ", ", ".join(missing_values)
            )

    dataframe_encoded = pd.DataFrame(dataframe)  # make a copy
    if not encoding_dictionary:
        encoding_dictionary = {
            value: i for i, value in enumerate(dataframe[column].unique())
        }
    dataframe_encoded[column_encoded] = dataframe_encoded[column].apply(
        lambda x: encoding_dictionary[x]
    )

    reversed_encoding_dict = reverse_dict(encoding_dictionary)

    return dataframe_encoded, reversed_encoding_dict
