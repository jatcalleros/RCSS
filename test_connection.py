import mysql.connector

try:
    connection = mysql.connector.connect(
        user='root',
        password='password',
        host='192.168.1.2',
        port=3306
    )

    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE mydatabase")

    print("Database created successfully!")
    connection.close()

except mysql.connector.Error as err:
    print(f"Something went wrong: {err}")

