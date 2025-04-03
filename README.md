# RFID-Based Access Control System

This project is an RFID-based access control system using a Raspberry Pi, Flask for the admin panel, and PostgreSQL for database management. The system allows administrators to manage users and their access roles through a web interface, while end devices verify RFID tags for granting or denying access.

## Features
- **Admin Panel (Flask Web App):**
  - View registered RFID tags and roles.
  - Add new users by scanning RFID cards and assigning roles.
  - User-friendly Bootstrap-based UI.
- **Access Control System (Raspberry Pi):**
  - Scans RFID cards using the MFRC522 module.
  - Checks access privileges in a PostgreSQL database.
  - Controls GPIO pins to activate LEDs for access granted/denied signals.
  
## Tech Stack
- **Back-end:** Flask (Python)
- **Database:** PostgreSQL
- **Hardware:** Raspberry Pi, MFRC522 RFID Reader, LEDs
- **Frontend:** HTML, Bootstrap

## Installation
### 1. Set Up Raspberry Pi
Ensure your Raspberry Pi is running Raspbian OS and has internet access.

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
SECRET_KEY=
DB_PASSWORD=
```

### 5. Configure PostgreSQL
Set up the PostgreSQL database and create a `users` table:
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    rfid_tag VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL
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

## Usage
- Use the web interface to register new users by scanning an RFID card and assigning a role.
- The Raspberry Pi will continuously scan for RFID tags and check their access level.
- If access is granted, the green LED will turn on; otherwise, the red LED will indicate denial.

## Future Improvements
- Add authentication to the admin panel.
- Hash values stored in database.
- Implement role-based access control for different areas.
- Enhance UI with additional filtering and sorting features.

## License
This project is open-source and available under the MIT License.

---
For any questions or contributions, feel free to open an issue or submit a pull request!

