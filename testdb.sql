create database event_hub;
use event_hub;
create table person (name varchar(20), age int);
insert into person values ('Alberto', 21);
select * from person where name = 'Alberto';