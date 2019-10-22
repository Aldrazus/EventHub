create database Event_Hub;
use Event_Hub;

create table User ( 
UserID int NOT NULL, 
UserName varchar(255) NOT NULL, 
Password varchar(255) NOT NULL, 
FirstName varchar(255) NOT NULL, 
LastName varchar(255) NOT NULL,
PRIMARY KEY (UserID, UserName) 
);


create table Student ( 
StudentID int, 
FOREIGN KEY (StudentID) REFERENCES User(UserID) 
);

create table Event_Organizer ( 
EventOrg_ID int, 
FOREIGN KEY (EventOrg_ID) REFERENCES User(UserID) 
);

create table Event (
EventID int NOT NULL,
EventName varchar(255) NOT NULL, 
OwnerID int,
PRIMARY KEY (EventID),
FOREIGN KEY (OwnerID) REFERENCES Event_Organizer(EventOrg_ID) 
);

