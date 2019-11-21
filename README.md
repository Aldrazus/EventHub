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
- Google Calendar API

## How to Run

1. Install the dependencies by entering `pip install -r requirements.txt`. If `requirements.txt` is not in the current directory, install each package manually by entering `pip install <package-name>`.
2. Install Elasticsearch and run it in the terminal. For instructions on how to install and run Elasticsearch, click here: https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
3. If the code was cloned straight from GitHub, run `flask db init`.
4. Make sure the database is up to date by running `flask db migrate` and `flask db upgrade`.
5. To run the Flask app, enter `flask run`.
6. Explore the features listed below.

Note: Test data was deliberately omitted from this application since any test data provided will not be indexed into Elasticsearch. This means that the test data would be unsearchable. Therefore, you must register your own users and create your own events.

## Features

### Login and Register
Users are able to register/log into their account. They may choose to register as a Student or Event Organizer

### Home Page / Friend and Global Feeds
Users are able to see when a friend (or any user) does a certain activity, such as creating an account or posting a new event.

### Profile Page
The profile page contains information about the user ('About Me'), their interests, and their recent activity. The events that they've created or followed can also be viewed, as well as their friends list.

### Event Feed
This feed displays a list of recently created events.

### Search Event
Users can search for events using the search bar. They can enter a topic or location into the main search bar to filter out events by topic or location. They can also select a time range to restrict the events by, or a specific school or college to search for events at that location. Note: the location selection will not filter out events that are not at that location, but the top search results will be events taking place at that location.

### Follow Event
Users can follow events to get notified of any updates.

### Search/Find Users
Users can search for other users by entering their username, first name, or last name. This is primarily used to find other users to friend.

### (Un)Friending
Users can send a friend request to other users they would like to be friends with. The other user may choose to accept or deny the friend request. Users can also unfriend friends. Users will be notified when their friends post an event.

### Posting/Updating Events
Event Organizers can post events, which notifies all friends. Event Organizers can also update event information, which will notify all followers of that event.

### Viewing Events
Users can view more information about an event, including certain statistics such as view count, follow count, and RSVP count

### Google Maps API
Users can view the location of an event on Google Maps.

### Google Calendar API
Users can add an event directly to their Google calendar.

### Notifications
Users will receive a notification when:
- they receive a friend request
- an event they've followed has been updated
- an event organizer they are friends with has posted an event

### Account
Users can modify their account info, such as their profile picture and about section. They can also make their email hidden to other users.