DROP TABLE IF EXISTS warehouseitems;

CREATE TABLE warehouseitems (
   location TEXT NOT NULL,
   description TEXT NOT NULL,
   amount INTEGER
);

DROP TABLE IF EXISTS users;

CREATE TABLE users (
   username TEXT NOT NULL,
   password TEXT NOT NULL

);

DROP TABLE IF EXISTS picklist;

CREATE TABLE picklist (
    picklistnumber INTEGER,
    assignto TEXT NOT NULL,
   location TEXT NOT NULL,
   description TEXT NOT NULL,
   amount INTEGER,
    collected BOOL
);
