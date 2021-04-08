from psycopg2.extensions import AsIs

# insert into table raw data in the database
def insert_raw_data_to_table(cursor, connection, file):
    for i in file:
        columns = i.keys()
        values = i.values()
        cursor = connection.cursor()
        query = "INSERT INTO pro.rawdata (%s) VALUES %s;"
        cursor.execute(query, (AsIs(','.join(columns)), tuple(values)))
    connection.commit()
    print("Raw data has been inserted.")

#insert data into orders
def insert_into_order(cursor, connection, normal2_list):
    for row in normal2_list:
        cursor.execute("""INSERT INTO pro.orders(date, location_id, payment_id, total_cost)
                            VALUES(DATE(%s), %s, %s, %s)""", (row["date"], row["location"], row["payment_method"], row["cost"]))
        connection.commit()

#insert data into location
def insert_into_location(cursor, connection, location_list):

    location_dict = {}
    for item in location_list:

        location_dict['id'] = item[1]
        location_dict['name'] = item[0]

    cursor.execute("""INSERT INTO pro.location(location_name)
                        VALUES('{}')""".format(location_dict['name']))
    connection.commit()

#insert data into paymets
def insert_into_payment(cursor, connection, pay_with_id):

    pay_dict = {}
    for lst in pay_with_id:

        pay_dict['id'] = lst[1]
        pay_dict['payment_type'] = lst[0]
    
        cursor.execute("""INSERT INTO pro.payment_type(type)
                            VALUES('{}')""".format(pay_dict['payment_type']))
        connection.commit()

#insert data into items
def insert_into_items(cursor, connection, items_list):

    for lst in items_list:

        item = lst[0] + lst[1]

        if '' in item:
            item.remove('')

        item = str(item)
        item = item[1:-1]
        item = item.replace(',','')
        item = item.replace("'","")

        for price in lst[2]:

            price = float(price)

        cursor.execute("""INSERT INTO pro.items(item_name, price)
                            VALUES(%s, %s)""", (item, price))
        connection.commit()

#inserts data into items orders table
def insert_into_item_order(cursor, connection):

    cursor.execute('SELECT ID, items FROM pro.rawdata')
    order_id_items = cursor.fetchall()

    order_id = 1
    for items in order_id_items:

        for i in items:

            if isinstance(i, str):
                i = i.split(',')

                for x in i:

                    try:
                        float(x)
                        i.remove(x)
                    except ValueError:
                        continue

                for x in i:

                    if x == '':
                        i.remove(x)

                for x in range(len(i)):

                    if i[x] == 'Large' or i[x] == 'Regular':
                        i[x] = i[x] + ' ' + i[x + 1]

                    if i[x - 1].startswith("Large") or i[x - 1].startswith("Regular"):
                        continue

                    cursor.execute(f'''SELECT item_id
                                        FROM pro.items
                                        WHERE item_name = '{i[x]}' ''')
                    item_id = cursor.fetchall()

                    item_id = str(item_id)
                    item_id = item_id.replace('[','')
                    item_id = item_id.replace(']','')

                    cursor.execute('''INSERT INTO pro.orders_items(order_id, item_id)
                                        VALUES(%s,%s)''', (order_id, item_id ))
                    connection.commit()

                order_id += 1