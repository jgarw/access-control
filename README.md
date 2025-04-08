# RFID-Based Access Control System

An RFID-based access control system using a Raspberry Pi and MFRC522 readers, with a Flask web interface for managing users and access roles. Role-based access is enforced per access point, and all data is stored in a PostgreSQL database.


## Features

### 🖥️ Admin Panel (Flask)
- View and manage registered users and their RFID tags.
- Add new users by scanning RFID cards and assigning roles.
- Define which roles are allowed at specific access points.
- Simple, responsive UI powered by HTML and Bootstrap.

### 📡 Access Control Script (Raspberry Pi)
- Supports **multiple RC522 readers** on a shared SPI bus using unique RST pins.
- Readers are activated one at a time to simulate parallel scanning.
- Access decisions are made by verifying the user’s role for the access point.
- Clean GPIO handling and SPI management to prevent interference.

## Tech Stack

| Layer        | Technology                        |
|--------------|------------------------------------|
| Back-End     | Python, Flask                      |
| Front-End    | HTML, Bootstrap                    |
| Database     | PostgreSQL                         |
| Hardware     | Raspberry Pi, MFRC522 RFID Readers |

## Setup

### 1. Hardware Setup & Wiring

Each MFRC522 RFID reader must share common SPI lines (SCK, MOSI, MISO), but must have a **unique RST pin** to allow selection of active readers via GPIO control.

| MFRC522 Unit | SCK (GPIO11) | MOSI (GPIO10) | MISO (GPIO9) | SDA (SS) | RST (unique GPIO) |
|--------------|--------------|---------------|--------------|----------|-------------------|
| Reader 1     | GPIO11       | GPIO10        | GPIO9        | GPIO8    | GPIO23            |
| Reader 2     | GPIO11       | GPIO10        | GPIO9        | GPIO8    | GPIO25            |

You may adjust the RST pins to your preferred available GPIOs. Only one reader should be active at a time.

### 2. Clone the Repository
```sh
git clone https://github.com/jgarw/access-control.git
cd access-control
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory and define the required environment variables:
```
DB_HOST="localhost"
DB_USER="postgres"
DB_PASSWORD="your_password"
DB_NAME="access_control"
DB_PORT="5432"
SECRET_KEY="your_secret_key"
```

### 5. Configure PostgreSQL
Set up the PostgreSQL database with the required tables:
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    rfid_tag VARCHAR(50) UNIQUE NOT NULL,
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
```

### 6. Run the Flask Admin Panel
```sh
python admin.py
```
The admin panel will be available at `http://localhost:5000/`.

### 7. Run the Access Control Script on Raspberry Pi
```sh
python app.py
```
This script will monitor all registered RFID readers and validate access based on roles.

## Usage
Use the admin panel to:
- Register users by scanning RFID cards and assigning roles.
- Set role permissions for specific access points (e.g., server room, lab).

The Raspberry Pi will:
- Read cards from each connected reader.
- Check the card's associated role and determine access permission.
- Print access logs to the console for now

## Future Improvements
- Add user authentication for admin panel.
- Add visual status indicators (e.g. LEDs, buzzers) for access granted/denied.
- Allow real-time monitoring of access events from the web panel.
- Log events in postgres database 

## License
This project is open-source and available under the MIT License.

---
For any questions or contributions, feel free to open an issue or submit a pull request!

