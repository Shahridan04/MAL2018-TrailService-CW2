-- 1. Create CW2 Schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'CW2')
BEGIN
    EXEC('CREATE SCHEMA [CW2]')
END
GO

-- 2. Create Users Table
CREATE TABLE CW2.[User] (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Email VARCHAR(100) NOT NULL UNIQUE,
    UserName VARCHAR(100) NOT NULL,
    Role VARCHAR(20) NOT NULL CHECK (Role IN ('Admin', 'User')),
    CreateDate DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- 3. Create Trail Table
CREATE TABLE CW2.Trail (
    TrailID INT IDENTITY(1,1) PRIMARY KEY,
    TrailName VARCHAR(100) NOT NULL,
    Length DECIMAL(5,2) NOT NULL CHECK (Length > 0),
    ElevationGain INT CHECK (ElevationGain >= 0),
    RouteType VARCHAR(50) NOT NULL CHECK (RouteType IN ('Loop', 'Out & Back', 'Point to Point')),
    Difficulty VARCHAR(20) NOT NULL CHECK (Difficulty IN ('Easy', 'Moderate', 'Hard')),
    Duration INT CHECK (Duration > 0),
    Description VARCHAR(MAX), -- Updated to MAX to match your App logic
    OwnerID INT NOT NULL,
    CreateDate DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (OwnerID) REFERENCES CW2.[User](UserID)
);
GO

-- 4. Create Audit Log Table (TrailLog)
CREATE TABLE CW2.TrailLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    TrailID INT,
    TrailName VARCHAR(100),
    OwnerID INT,
    OwnerName VARCHAR(100),
    ActionType VARCHAR(20) NOT NULL CHECK (ActionType IN ('INSERT', 'UPDATE', 'DELETE')),
    ActionDate DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- 5. Create Trigger for Logging (From your Exercise 7)
CREATE TRIGGER CW2.trg_LogNewTrail
ON CW2.Trail
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO CW2.TrailLog (TrailID, TrailName, OwnerID, OwnerName, ActionType)
    SELECT 
        i.TrailID,
        i.TrailName,
        i.OwnerID,
        u.UserName,
        'INSERT'
    FROM inserted i
    INNER JOIN CW2.[User] u ON i.OwnerID = u.UserID;
END;
GO

-- 6. Insert Required Users (From Assessment Brief)
INSERT INTO CW2.[User] (Email, UserName, Role) VALUES
('grace@plymouth.ac.uk', 'Grace Hopper', 'Admin'),
('tim@plymouth.ac.uk', 'Tim Berners-Lee', 'Admin'),
('ada@plymouth.ac.uk', 'Ada Lovelace', 'User');
GO
