import sqlite3
import os
from typing import List, Dict, Tuple, Union
from DatabaseHandler.config import *


def create_database_and_table():
    """creates the needed table """

    with sqlite3.connect(database_name) as conn:
            # print("INItial running database")
            cursor = conn.cursor()
            cursor.execute(document_table_creation_script)
            cursor.execute(unverified_document_table_creation_script)
            cursor.execute(user_table_script)

def executeNonSelectQuery(query: str, values: Tuple[Union[str, int, float]] = None):
    """used to execute insert, update and delete functions.

    Args:
        query (str): query
        values (Tuple[Union[str, int, float]]): values to be used. Defaults to None
    """
    # try:
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
    # except sqlite3.Error as e:
    #     print(f"Error executing non-select query: {e}")


def executeQueryAndReturnJson(query: str) -> List[Dict]:
    """used to run select statements and fetch result

    Args:
        query (str): the query to run

    Returns:
        List[Dict]: each item is a key value pair of field and its value
        
    """
    try:
        with sqlite3.connect(database_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            final_result = []
            for res in cursor.fetchall():
                temp = dict(zip(columns, res))
                final_result.append(temp.copy())
            return final_result
    except sqlite3.Error as e:
        print(f"Error executing select query: {e}")
        return []


create_database_and_table()