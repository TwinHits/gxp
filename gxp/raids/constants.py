class ValidationErrors:
    INVALID_ID = "This id is not a UUID vr id."
    NAME_ALREADY_EXISTS = "A raider by this name already exists."
    INVALID_CHARACTER_NAME = "This is not a valid character name, length must be between 2 and 12 characters."
    INVALID_WARCRAFT_LOGS_ID = "This is not a valid Warcraft logs id."
    WARCRAFT_LOGS_ID_RAID_ALREADY_EXISTS = (
        "A raid with this warcraft logs id already exists."
    )
    WARCRAFT_LOGS_ID_LOG_ALREADY_EXISTS = (
        "A log with this warcraft logs id already exists."
    )
    LOG_INACTIVE = "This log is inactive and cannot be used to create a raid."
    RAIDER_DOES_NOT_EXIST = "This raider does not exist."
    RAIDER_IS_AN_ALT = "This raider is an alt."
