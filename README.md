# Event Hub

## Dependencies

- Python 3
- Flask
- PyMySQL
- MySQL Server

## How to Run

1. Configure your MySQL server. Make sure the user is 'root' and the password is 'password'.
2. Run the MySQL script named _testdb.sql_. This creates a database named _event_hub_, creates a table named _Person_ with fields _name_ and _age_, adds an entry to this table, and queries for this entry. **Make sure this works before proceeding to the next step.**
3.  In the command line, go to the _EventHub_ directory and enter `python main.py`.
4.  In your web browser, go to `localhost:5000`. You should see text that says "_Hello World! Alberto's is 21 years old_".