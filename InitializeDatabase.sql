/*Statements to create database and tables**/

/*Creates Database**/
CREATE DATABASE TruckTracker;

/*Create USER table**/
CREATE TABLE USER(
  UserID int NOT NULL AUTO_INCREMENT,
  FirstName varchar(30) NOT NULL,
  LastName varchar(30) NOT NULL,
  HashPwd varchar(64) NOT NULL,
  UserType varchar(8) NOT NULL,
  CONSTRAINT UserPK PRIMARY KEY(UserID)
);
