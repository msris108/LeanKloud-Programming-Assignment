import json
import sqlite3

con = sqlite3.connect('workspace.db')

cur = con.cursor()

# Create table
# cur.execute("CREATE TABLE todos(id real, task text, status text, date text)")

# Delete a row 
# cur.execute("DELETE FROM todos WHERE id=1")

# Insert a row of data
# cur.execute("INSERT INTO todos VALUES ('1', 'Task 1', 'Finished', '2021-05-01')")
# cur.execute("INSERT INTO todos VALUES ('2', 'Task 2', 'Finished', '2021-05-21')")
# cur.execute("INSERT INTO todos VALUES ('3', 'Task 3', 'In Progress', '2021-05-13')")
# cur.execute("INSERT INTO todos VALUES ('4', 'Task 4', 'Not Started', '2021-04-05')")
# cur.execute("INSERT INTO todos VALUES ('5', 'Task 5', 'Not Started', '2012-07-05')")


# Save (commit) the changes
# con.commit()

# for row in cur.execute('SELECT * FROM todos'):
# 	print(row)

x = cur.execute('SELECT * FROM todos').fetchone()
print(json.dumps(x))

print("Total Records: ", cur.execute('SELECT COUNT(*) AS count FROM todos').fetchone()[0])

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()