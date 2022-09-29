import psycopg2

def get_connection():
    try:
        return psycopg2.connect(
            database='testdb',
            user='postgres',
            password='postgres',
            host='127.0.0.1',
            port=5432
        )
    except:
        return False

conn = get_connection()

if conn:
    print("Connection to the PostgreSQL established successfully.")
else:
    print("Connection to the PostgreSQL encountered and error.")

conn = get_connection()
curr = conn.cursor()

query = '''
CREATE TABLE Offers (
	ID SERIAL PRIMARY KEY,
	DownloadDate DATE NOT NULL,
	PostedDate DATE,
	ExternalID CHAR(8) NOT NULL UNIQUE,
	Title VARCHAR(100) NOT NULL,
	Category VARCHAR(50),
	URL VARCHAR(150),
	CompanySize INT,
	SalaryCurrency CHAR(3),
	SalaryMinUoP MONEY,
	SalaryMaxUoP MONEY,
	SalaryMinB2B MONEY,
	SalaryMaxB2B MONEY,
	SalaryMinOther MONEY,
	SalaryMaxOther MONEY,
	AvailableRemote BOOLEAN,
	AvailableInPoland BOOLEAN
)
'''

curr.execute(query)

# data = curr.fetchall()
#
#
# for row in data:
#     print(row)


conn.close()
