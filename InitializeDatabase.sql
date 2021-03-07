/*Statements to create database and tables*/

/*Creates Database*/
CREATE DATABASE TruckTracker;

/*Uses database to add tables*/
USE TruckTracker;

/*Create USER table
*UserID will be automatically incremented
*Password stored as SHA256 hash digest
*/
CREATE TABLE USER(
  UserName varchar(10) NOT NULL,
  FirstName varchar(30) NOT NULL,
  LastName varchar(30) NOT NULL,
  HashPwd varchar(64) NOT NULL,
  UserType varchar(8) NOT NULL,
  CONSTRAINT UserPK PRIMARY KEY (UserName)
);

/*Create VEHICLE table
*Type can be Truck or Trailer
*Deleting vehicle will delete everything associated with that vehicle
*/
CREATE TABLE VEHICLE(
  VehicleID varchar(10) NOT NULL,
  Mileage int NOT NULL,
  VehileType varchar(8) NOT NULL,
  VIN int NOT NULL,
  LicensePlate varchar(8) NOT NULL,
  CONSTRAINT VehiclePK PRIMARY KEY (VehicleID)
);

/*Create SERVICE table
*/
CREATE TABLE SERVICE(
  ServiceName varchar(30) NOT NULL,
  ServiceDescription varchar(280) NULL,
  CONSTRAINT ServicePK PRIMARY KEY (ServiceName)
);

/*Create MAINTENANCE_ENTRY table
*Deleting a user will not delete entries, but deleting an entry will remove notes
*/
CREATE TABLE MAINTENANCE_ENTRY(
  EntryID int NOT NULL,
  Vehicle int NOT NULL,
  EntryDate date NOT NULL,
  MileageAtTime int NOT NULL,
  Requester varchar(10) NULL,
  Mechanic varchar(10) NULL,
  CONSTRAINT MaintenanceEntryPK PRIMARY KEY (EntryID),
  CONSTRAINT RequesterFK FOREIGN KEY (Requester) REFERENCES USER(UserName) ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT MechanicFK FOREIGN KEY (Mechanic) REFERENCES USER(UserName) ON UPDATE CASCADE ON DELETE SET NULL
);

/*Create SERVICE_JUNCTION table
*Deleting entry or service will delete associated realtionships
*/
CREATE TABLE SERVICE_JUNCTION(
  Entry int NOT NULL,
  Service varchar(30) NOT NULL,
  CONSTRAINT ServiceJunctionPK PRIMARY KEY (Entry, Service),
  CONSTRAINT EntryFK1 FOREIGN KEY (Entry) REFERENCES MAINTENANCE_ENTRY(EntryID) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT ServiceFK FOREIGN KEY (Service) REFERENCES SERVICE(ServiceName) ON UPDATE CASCADE ON DELETE CASCADE
);

/*Create NOTE table
*/
CREATE TABLE NOTE(
  NoteID int NOT NULL,
  NoteText varchar(280) NOT NULL,
  NoteDate date NOT NULL,
  Entry int NOT NULL,
  User varchar(10) NULL,
  CONSTRAINT EntryFK2 FOREIGN KEY (Entry) REFERENCES MAINTENANCE_ENTRY(EntryID) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT UserFK FOREIGN KEY (User)  REFERENCES USER(UserName) ON UPDATE CASCADE ON DELETE SET NULL
);
