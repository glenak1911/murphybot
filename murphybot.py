import os
import json
import requests
import pymysql.cursors
import sys

def handler(event, context):
    # Grab webhook url
    webhook_url = os.environ['WEBHOOK_URL']

    slack_acknowledgement = requests.post(
      webhook_url, 
      data={"text":""},
      headers={'Content-Type': 'application/json'}
    )

    connection = connectToDb()

    result = getMessage(connection)
    
    print("result: {}".format(result))

    law = result["Title"]

    print("sending {} data to: {}".format(law, webhook_url))

    response_data = json.dumps({"text":"{}".format(law)})

    postToSlack(response_data, webhook_url)

    return { "isBase64Encoded": True, "statusCode": 200, "headers": { }, "body": "" }

def connectToDb():
    connection = pymysql.connect(host=os.environ['DB_ENDPOINT'],
                                 user=os.environ['DB_USER'],
                                 password=os.environ['DB_PASSWORD'],
                                 db='murphyslaws',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    print("connection info: {}".format(connection))

    return connection

def getMessage(db_connection):
    try:
        with db_connection.cursor() as cursor:
            sql = "SELECT * FROM laws ORDER BY RAND() LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
    finally:
        db_connection.close()

    return result

def postToSlack(response_data, webhook_url):
    slack_message = requests.post(
      webhook_url, 
      data=response_data,
      headers={'Content-Type': 'application/json'}
    )
