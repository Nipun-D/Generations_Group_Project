import boto3
import os
import sys
import csv
import psycopg2
import psycopg2.extras
import uuid
import datetime

def remove_sensitive_data(file):
    for row in file:
        del row['customer']
        del row['card_number']
    return file

def create_basket_data(basket):
    basketitems = []
    splitvalue = basket.split(",")
    for item in splitvalue:
        basket = {}
        if item.count("-") == 1:
            splitval = item.split("-")
            if "Large" in item:
                basket["item_size"] = "Large"
                name = splitval[0].replace("Large", "").strip()
                basket["item_name"] = name
            else:
                basket["item_size"] = "Regular"
                name = splitval[0].replace("Regular", "").strip()
                basket["item_name"] = name
            basket["item_price"] = float(splitval[1])
        elif item.count("-") == 2:
            splitval = item.rsplit("-", 1)
            basket["item_price"] = float(splitval[1])
            if "Large" in item:
                basket["item_size"] = "Large"
                name = splitval[0].replace("Large", "").strip()
                basket["item_name"] = name
            else:
                basket["item_size"] = "Regular"
                name = splitval[0].replace("Regular", "").strip()
                basket["item_name"] = name
        basketitems.append(basket)
    return basketitems

def create_transaction_data(data):
    transactions = []
    for transaction in data:
        temp_transaction = {
            "transaction_id" : str(uuid.uuid4()),
            "date" : datetime.datetime.strptime(transaction['date'], '%d/%m/%Y %H:%M'),
            "location" : transaction["location"],
            "basket_items" : create_basket_data(transaction["items"]),
            "payment_type" : transaction["payment_type"],
            "cost" : transaction["cost"]
        }
        transactions.append(temp_transaction)
    return transactions

def load(transactions):
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    user = os.getenv("DB_USER")
    db = os.getenv("DB_NAME")
    cluster = os.getenv("DB_CLUSTER")

    #Get cluster credentials
    try:
        client = boto3.client('redshift')
        creds = client.get_cluster_credentials(
            DbUser=user,
            DbName=db,
            ClusterIdentifier=cluster,
            DurationSeconds=3600
        )
    except Exception as e:
        print(e)
        sys.exit(1)

    #Create object connection to redshift
    try:
        conn = psycopg2.connect(
            dbname=db,
            user=creds["DbUser"],
            password=creds["DbPassword"],
            port=port,
            host=host)
    except Exception as e:
        print(e)
        sys.exit(1)

    #Load data into transaction table
    with conn.cursor() as cursor:
        psycopg2.extras.execute_values(cursor, """
                INSERT INTO transactions (transaction_id, date, location, payment_type, cost) VALUES %s;
            """, [(
                t['transaction_id'],
                t['date'],
                t['location'],
                t['payment_type'],
                t['cost']
            )for t in transactions],
            template='(%s,%s,%s,%s,%s)')

        #Load data into basket table
        for t in transactions:
            psycopg2.extras.execute_values(cursor, """
                    INSERT INTO basket(transaction_id, item_name, item_size, item_price) VALUES %s;
                """, [(
                    t['transaction_id'],
                    b['item_name'],
                    b['item_size'],
                    b['item_price']
                ) for b in t['basket_items']],
                template='(%s,%s,%s,%s)')
    conn.commit()

def handle(event, context):
    #List all files in bucket
    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    #Get_csv_data_from_bucket
    s3 = boto3.client('s3')
    s3_object = s3.get_object(Bucket = bucket, Key = key)
    data = s3_object['Body'].read().decode('utf-8')
    headers = ["date", "location", "customer", "items",  "cost", "payment_type", "card_number"]
    csv_data = csv.DictReader(data.splitlines(), headers)
    csv_list_data = []
    for item in csv_data:
        csv_list_data.append(dict(item))

    file = remove_sensitive_data(csv_list_data)
    transactions = create_transaction_data(file)
    load(transactions)
    return

