CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    rfid_tag VARCHAR(64) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE access_permissions (
    access_point_id VARCHAR(50),  
    allowed_role VARCHAR(50),    
    PRIMARY KEY (access_point_id, allowed_role)
);

CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rfid_tag VARCHAR(64),
    reader_id VARCHAR(50),
    result VARCHAR(50),
    message TEXT
);