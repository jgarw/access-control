# RFID-Based Access Control System

This project is an RFID-based access control system using a Raspberry Pi, Flask for the admin panel, and PostgreSQL for database management. The system allows administrators to manage users and their access roles through a web interface, while end devices verify RFID tags for granting or denying access.

## Features
- **Admin Panel (Flask Web App):**
  - View registered RFID tags and their assigned roles.
  - Add new users by scanning RFID cards and assigning roles.
  - Bootstrap-based UI for easy management.
- **Access Control System (Raspberry Pi):**
  - Supports multiple MFRC522 RFID readers via SPI switching.
  - Role-based access permissions per reader.
  - PostgreSQL-backed permission verification.

## Tech Stack
- **Back-end:** Flask (Python)
- **Database:** PostgreSQL
- **Hardware:** Raspberry Pi, MFRC522 RFID Readers, LEDs
- **Frontend:** HTML, Bootstrap

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
- Use the web interface to register new users by scanning an RFID card and assigning a role.
- Use the `access_permissions` table to define which roles can access specific points (e.g., doors, rooms).
- The Raspberry Pi script reads RFID tags and validates them against both the `users` and `access_permissions` tables.
- Access attempts are logged in the `access_logs` table for review.

## Future Improvements
- Add user authentication for admin panel.
- Add visual status indicators (e.g. LEDs, buzzers) for access granted/denied.
- Allow real-time monitoring of access events from the web panel.
- Enable dynamic assignment of multiple roles per user.
- Export access logs to CSV or Excel.

## License
This project is open-source and available under the MIT License.

---
For any questions or contributions, feel free to open an issue or submit a pull request!

