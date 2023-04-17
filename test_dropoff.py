from sqlalchemy import create_engine, text
import datetime

# Set up database connection
db_uri = 'mysql+pymysql://phpmyadmin:password@192.168.1.2/RCSS'
engine = create_engine(db_uri)

# Insert new entry into student_dropoff table
with engine.connect() as conn:
    stmt = text("INSERT INTO student_dropoff (student_id_fk, dropoff_time) VALUES (:student_id_fk, :dropoff_time)")
    result = conn.execute(stmt, {"student_id_fk": 852776988675, "dropoff_time": datetime.datetime.now()})
    conn.commit()  # Commit the transaction
    print("Number of rows inserted: ", result.rowcount)
