-- 1. Create Trail Procedure
CREATE PROCEDURE CW2.sp_CreateTrail
    @TrailName VARCHAR(100),
    @Length DECIMAL(5,2),
    @ElevationGain INT,
    @RouteType VARCHAR(50),
    @Difficulty VARCHAR(20),
    @Duration INT,
    @Description VARCHAR(MAX),
    @OwnerID INT
AS
BEGIN
    SET NOCOUNT ON;
    -- Check if owner exists
    IF NOT EXISTS (SELECT 1 FROM CW2.[User] WHERE UserID = @OwnerID)
    BEGIN
        RAISERROR('Invalid OwnerID.', 16, 1);
        RETURN;
    END

    INSERT INTO CW2.Trail (TrailName, Length, ElevationGain, RouteType, Difficulty, Duration, Description, OwnerID)
    VALUES (@TrailName, @Length, @ElevationGain, @RouteType, @Difficulty, @Duration, @Description, @OwnerID);
    
    SELECT SCOPE_IDENTITY() AS NewTrailID;
END;
GO

-- 2. Get All Trails Procedure
CREATE PROCEDURE CW2.sp_GetAllTrails
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM CW2.Trail ORDER BY TrailName;
END;
GO

-- 3. Get Trail By ID Procedure
CREATE PROCEDURE CW2.sp_GetTrailByID
    @TrailID INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM CW2.Trail WHERE TrailID = @TrailID;
END;
GO

-- 4. Update Trail Procedure
CREATE PROCEDURE CW2.sp_UpdateTrail
    @TrailID INT,
    @TrailName VARCHAR(100),
    @Length DECIMAL(5,2),
    @ElevationGain INT,
    @RouteType VARCHAR(50),
    @Difficulty VARCHAR(20),
    @Duration INT,
    @Description VARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE CW2.Trail
    SET TrailName = @TrailName,
        Length = @Length,
        ElevationGain = @ElevationGain,
        RouteType = @RouteType,
        Difficulty = @Difficulty,
        Duration = @Duration,
        Description = @Description
    WHERE TrailID = @TrailID;
END;
GO

-- 5. Delete Trail Procedure (With Log Logic included)
CREATE PROCEDURE CW2.sp_DeleteTrail
    @TrailID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Log the deletion manually before deleting
    INSERT INTO CW2.TrailLog (TrailID, TrailName, OwnerID, OwnerName, ActionType)
    SELECT 
        t.TrailID, t.TrailName, t.OwnerID, u.UserName, 'DELETE'
    FROM CW2.Trail t
    JOIN CW2.[User] u ON t.OwnerID = u.UserID
    WHERE t.TrailID = @TrailID;

    DELETE FROM CW2.Trail WHERE TrailID = @TrailID;
END;
GO
