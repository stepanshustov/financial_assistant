import sqlite3

con = sqlite3.connect('users.sqlite')
cur = con.cursor()
cur.execute("""INSERT INTO log_pass(login, password, balance) VALUES('petya', '654321', 555.56)""")
