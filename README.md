# Event Hub

## Dependencies

- Python 3
- Flask
- Flask-Login
- Flask-Migrate
- Flask-SQLAlchemy
- Flask-WTF & WTForms
- python-dotenv
- MySQL Server
- Elasticsearch
- Flask-Moment

## How to Run

1. Install the dependencies by entering `pip install -r requirements.txt`. If `requirements.txt` is not in the current directory, install each package manually by entering `pip install <package-name>`.
2. Install Elasticsearch and run it in the terminal. For instructions on how to install and run Elasticsearch, click here: https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
3. Make sure the database is up to date by running `flask db migrate` and `flask db upgrade`. 
4. To run the Flask app, enter `flask run`. 