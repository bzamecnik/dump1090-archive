CREATE ROLE dump1090 WITH LOGIN PASSWORD 'dump1090.password.change.this';

CREATE DATABASE dump1090 OWNER dump1090 TEMPLATE template0;

\c dump1090

CREATE TABLE messages (
    ReceiverId varchar(12),
    MessageType varchar(3),
    TransmissionType smallint,
    SessionID smallint,
    AircraftID smallint,
    HexIdent varchar(6),
    FlightID integer,
    DateMessageGenerated varchar(10),
    TimeMessageGenerated varchar(12),
    DateMessageLogged varchar(10),
    TimeMessageLogged varchar(12),
    Callsign varchar(8),
    Altitude integer,
    GroundSpeed numeric(5, 1),
    Track varchar(8),
    Latitude numeric(8, 5),
    Longitude numeric(8, 5),
    VerticalRate varchar(8),
    Squawk varchar(8),
    Alert varchar(8),
    Emergency varchar(8),
    SPI varchar(8),
    IsOnGround smallint
);

GRANT ALL ON messages TO dump1090;
