Python packages required:
- sqlite3
- SimpleCV
- zbarlight

Database Setup:
1- Change directory to the location, where Python code is deployed.
2- Create sqlite Attendance database using the following commands:
    - sqlite3
    - CREATE database attendance.db;
3- Create Attendance table in the newly created database:
    CREATE TABLE ATTENDANCE(
        ID CHAR(24) PRIMARY KEY NOT NULL,
        SCAN_TIME   DATETIME    NOT NULL,
        PRESENT_FLG INT         NOT NULL,
        SYNC_FLG    INT         NOT NULL
    );
4- Run scan_qr.py to begin scanning QR Codes.