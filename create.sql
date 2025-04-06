CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    rfid_tag VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE access_permissions (
    access_point_id VARCHAR(50),  -- e.g. "door1", "lab_entry", etc.
    allowed_role VARCHAR(50),     -- e.g. "Engineer", "Supervisor"
    PRIMARY KEY (access_point_id, allowed_role)
);