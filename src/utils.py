from io import StringIO
import json
import pandas as pd
from loguru import logger


def convert_html_table(table: list[object]) -> pd.DataFrame:
    """
    Converts an HTML table into a pandas DataFrame.
    Args:
        table (list[object]): A list containing the HTML table as a string.
    Returns:
        pandas.DataFrame: A DataFrame representation of the HTML table with
        column names converted to lowercase and spaces replaced by underscores.
        Returns an empty DataFrame if the input table is invalid or empty.
    Raises:
        ValueError: If the input table cannot be parsed into a DataFrame.
    """

    list_df_table = pd.read_html(StringIO(table))

    if list_df_table:
        df_table = list_df_table[0]
        df_table.columns = [col.replace(" ", "_").lower() for col in df_table.columns]
        return df_table

    return pd.DataFrame()


def json_write(fname: str, data: dict) -> bool:
    """
    Writes a dictionary to a JSON file.
    Args:
        fname (str): The file path where the JSON data will be written.
        data (dict): The dictionary to be serialized and written to the file.
    Returns:
        bool: True if the operation is successful, False otherwise.
    Raises:
        TypeError: If the provided data is not serializable to JSON.
        IOError: If an error occurs while writing to the file.
        Exception: For any other unexpected errors.
    """

    try:
        with open(fname, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file)
        return True
    except TypeError as e:
        error = f"TypeError: Data provided is not serializable to JSON. {e}"
    except IOError as e:
        error = f"IOError: An error occurred while writing to the file. {e}"
    except Exception as e:
        error = f"Unexpected error: {e}"

    logger.error(error)
    return False
