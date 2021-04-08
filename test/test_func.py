from src.app import remove_sensitive_data, extract_csv, connect_to_database, create_schema_for_database, create_raw_data_table, insert_raw_data_to_table
from unittest.mock import patch
import psycopg2

def test_remove_sensitive_data():

    # arrange
    list_dict = [{
        'id': 1,
        'customer': None,
        'card_number':None
    }]

    expected = [{'id':1}]
    actual = remove_sensitive_data(list_dict) # actual which should equal the mock (list_dict)

    assert expected == actual # assert which should equal the actual
    print(expected == actual) # print to test it, see if it works

@patch("builtins.print")
def test_extract_csv(mock_print):
    #happy path
    # file_path = "test.csv"
    
    # expected = []
    
    # actual = extract_csv(file_path) 

    # assert expected == actual

    #unhappy path

    file = ''
    extract_csv(file)
    mock_print.assert_called_with('Failed to open file.')

@patch("builtins.print")
def test_create_raw_data_table(mock_print):
    cursor, connection = connect_to_database()

    #Happy path
    create_raw_data_table(cursor)
    mock_print.assert_called_with("Table created successfully")

    #Unhappy path
    fake_cursor = ""
    create_raw_data_table(fake_cursor)
    mock_print.assert_called_with("Table could not be created.")

def test_connect_to_datbase():

    params = {
        'dbname': 'transactions',
        #'username': 'root',
        'password': 'password',
        'host': 'postgres',
        'port': 5432
    }
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    expected = (cursor, connection)
    actual = (connect_to_database())

    assert actual == expected

