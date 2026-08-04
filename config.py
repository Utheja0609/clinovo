import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="uthej@123",      # Put your MySQL password here if you have one
    database="clinovo_assessment"
)

cursor = db.cursor(dictionary=True)