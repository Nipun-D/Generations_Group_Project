import csv
import psycopg2
import psycopg2.extras
import normalise
import load


#-----------------------------------------------------------------------------------
# CSV
isle_wight_csv_list = []
file_path = './src/data/2021-02-23-isle-of-wight.csv'
def extract_csv(file_path):
    try:
        with open(file_path, "r") as isle_wight_file:
            data_in_file = csv.DictReader(isle_wight_file)
            for row in data_in_file:
                isle_wight_csv_list.append(row)
    except:
        print('Failed to open file')
    return isle_wight_csv_list


# remove sensitive data
def remove_sensitive_data(file):
    for row in file:
        del row['customer']
        del row['card_number']
    return file

#-----------------------------------------------------------------------------------------------
# SQL

# connection
def connect_to_database():
    params = {
        'dbname': 'transactions',
        #'username': 'root',
        'password': 'password',
        'host': 'postgres',
        'port': 5432
    }
    connection = psycopg2.connect(**params)
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    return cursor, connection

# create schema
def create_schema_for_database(cursor):
    cursor.execute("CREATE SCHEMA IF NOT EXISTS pro")
    print("Schema was created.")

# drops all tables from the database
def drop_all_tables(cursor):
    try:
        cursor.execute("""
        DROP TABLE IF EXISTS pro.orders_items;
        DROP TABLE IF EXISTS pro.orders;
        DROP TABLE IF EXISTS pro.items;
        DROP TABLE IF EXISTS pro.rawdata;
        DROP TABLE IF EXISTS pro.location;
        DROP TABLE IF EXISTS pro.payment_type;
        """)
        print("Existing tables have been dropped.")
    except:
        print("Tables have not been dropped.")

# create raw data table in the database
def create_raw_data_table(cursor):
    try:
        cursor.execute('''CREATE TABLE pro.rawdata
            (ID SERIAL PRIMARY KEY,
            date DATE,
            location VARCHAR(255),
            items VARCHAR(255),
            payment_method VARCHAR(255),
            cost FLOAT);''')
        print("Raw data table created successfully.")
    except:
        print("Raw data table could not be created.")

# create order table in the database
def create_order_table(cursor):
    try:
        cursor.execute('''CREATE TABLE pro.orders
            (order_id SERIAL PRIMARY KEY,
            date DATE,
            location_id INT,
            FOREIGN KEY(location_id) REFERENCES pro.location(location_id),
            payment_id INT,
            FOREIGN KEY(payment_id) REFERENCES pro.payment_type(payment_type_id),
            total_cost FLOAT
            );''')
        print("Order table created successfully.")
    except Exception as e:
        print(f"Order table could not be created. {e}")

# create items table in the database
def create_items_table(cursor):
    try:
        cursor.execute('''CREATE TABLE pro.items
            (item_id SERIAL PRIMARY KEY,
            item_name VARCHAR(255),
            price FLOAT);''')
        print("Item table created successfully.")
    except:
        print("Item table could not be created.")

# create payment type table in the database
def create_payment_type_table(cursor):
    try:
        cursor.execute('''CREATE TABLE pro.payment_type
            (payment_type_id SERIAL PRIMARY KEY,
            type VARCHAR(255)
            );''')
        print("Payment table created successfully.")
    except:
        print("Payment table could not be created.")

# create location table in the database
def create_location_table(cursor):
    try:
        cursor.execute('''CREATE TABLE pro.location
            (location_id SERIAL PRIMARY KEY,
            location_name VARCHAR(255)
            );''')
        print("Location table created successfully.")
    except:
        print("Location table could not be created.")

# intermediary table
def create_item_order_table(cursor):
    try:
        cursor.execute('''CREATE TABLE pro.orders_items
            (order_id INT NOT NULL,
            FOREIGN KEY(order_id) REFERENCES pro.orders(order_id),
            item_id INT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES pro.items(item_id)
            );''')
        print("Order and item tables were created successfully.")
    except:
        print("Order and item tables could not be created. ")


#extracting data
file = extract_csv(file_path)
file = remove_sensitive_data(file)

#normalising data
not_normal_list, first_item = normalise.seprating_lines(file, "items") # importing func from normalise - why is items in quotation marks?
not_normal_list2 = normalise.creating_list_without_item(file)
items = normalise.finding_unique_value(first_item) # importing func from normalise
items_list = normalise.adding_id(items) # importing func from normalise
normal_list = normalise.creating_list_with_item_id(not_normal_list, items_list) # importing func from normalise
pay_list = normalise.extracting_lists(not_normal_list2, "payment_method")
location_list = normalise.extracting_lists(not_normal_list2, "location")
pay_with_id = normalise.adding_id(pay_list)
location_with_id = normalise.adding_id(location_list)
normal2_list = normalise.creating_list_with_replacing_id(not_normal_list2, pay_with_id, "payment_method", 1)
normal3_list = normalise.creating_list_with_replacing_id(not_normal_list2, location_with_id, "location", 1)

# for row in normal3_list:
#     print(row)

#create connection
cursor, connection = connect_to_database()

#build database
create_schema_for_database(cursor)
drop_all_tables(cursor)
create_raw_data_table(cursor)
create_items_table(cursor)
create_payment_type_table(cursor)
create_location_table(cursor)
create_order_table(cursor)
create_item_order_table(cursor)

#insert data into tables
load.insert_raw_data_to_table(cursor, connection, file)
load.insert_into_location(cursor, connection, location_list)
load.insert_into_payment(cursor, connection, pay_with_id)
load.insert_into_order(cursor, connection, normal2_list)
load.insert_into_items(cursor, connection, items_list)
load.insert_into_item_order(cursor, connection)
uniqe_location = normalise.finding_unique_location(not_normal_list)

for i in uniqe_location:
    print(i)
    print(type(i))
print(type(uniqe_location))

connection.close()
