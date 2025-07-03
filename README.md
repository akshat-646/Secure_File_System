Secure File System with Biometric and Database Authentication
This project implements a secure file system with a graphical user interface (GUI) built using Tkinter, featuring user authentication via both traditional username/password and biometric (face recognition) methods. It integrates with a MySQL database for user management and a custom C module for secure file operations.

Features
User Registration & Login: Secure user registration and login with username, password, and role (user/admin).

Biometric Authentication: Face recognition integrated into the login process for an additional layer of security.

Role-Based Access Control:

User Role: Can create, read, and write to their own secure files.

Admin Role: Has all user privileges, plus the ability to access all files in the system and manage users (view, delete).

Secure File Operations: Create, read, and write text files within a designated "secure folder."

Database Integration: Uses MySQL to store user credentials (hashed passwords), roles, face image paths, and login attempt logs.

Custom C Module Integration: A C program handles the low-level file operations within the secure folder, compiled and executed from the Python GUI.

Login Attempt Logging: Records login attempts for security monitoring.

Theme Toggle: Switch between light and dark modes for the GUI.

Camera Test Utility: A utility to test camera functionality for face recognition.

System Architecture
The system is composed of four main components:

gui.py: The main Python script for the Tkinter-based graphical user interface. It handles user interactions, authentication flow, and calls to other modules.

face_module.py: A Python module responsible for face capture and verification using opencv and face_recognition libraries.

database_setup.py: A Python module for managing the MySQL database, including creating the database/tables, registering users, verifying credentials, and logging login attempts.

secure_os_module.c: A C program that performs the actual file operations (create, read, write, access all files) within the secure folder. This module is called as a subprocess from gui.py.

Prerequisites
Before running the application, ensure you have the following installed:

Python 3.x

MySQL Server: [suspicious link removed]

C Compiler: A C compiler like MinGW (for Windows) or GCC (for Linux/macOS) to compile secure_os_module.c.

Python Libraries:

mysql-connector-python

opencv-python

face_recognition

Pillow (PIL)

You can install the Python libraries using pip:

pip install mysql-connector-python opencv-python face_recognition Pillow

Setup Instructions
1. MySQL Database Setup
Start MySQL Server: Ensure your MySQL server is running.

Configure database_setup.py:

Open database_setup.py.

Modify user and password in create_database_connection() and create_database_and_tables() functions to match your MySQL root (or a user with database creation privileges) username and password. By default, they are set to 'root' and 'root'.

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='secure_file_system', # This database will be created
            user='your_mysql_user',       # <--- CHANGE THIS
            password='your_mysql_password' # <--- CHANGE THIS
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

Run Database Setup Script: Execute database_setup.py once to create the database and necessary tables.

python database_setup.py

You should see a message like "✅ Database and tables created successfully!".

2. Compile C Module
Open a Terminal/Command Prompt: Navigate to the directory where secure_os_module.c is located.

Compile the C code:

On Windows (using MinGW/GCC):

gcc secure_os_module.c -o secure_os_module.exe -lws2_32 -luser32

On Linux/macOS (using GCC):

gcc secure_os_module.c -o secure_os_module

This will create an executable file (secure_os_module.exe on Windows, secure_os_module on Linux/macOS).

3. Configure Secure Folder Path
Update CUSTOM_FOLDER:

Open both gui.py and secure_os_module.c.

Locate the CUSTOM_FOLDER definition in both files.

It is crucial that this path is identical in both files. Change it to your desired secure folder location. For example:

gui.py:

CUSTOM_FOLDER = r"C:\path\to\your\secure_folder" # Windows example
# or for Linux/macOS: CUSTOM_FOLDER = "/home/user/secure_folder"

secure_os_module.c:

#define CUSTOM_FOLDER "C:\\path\\to\\your\\secure_folder" // Windows example (note double backslashes)
// or for Linux/macOS: #define CUSTOM_FOLDER "/home/user/secure_folder"

Important for Windows paths in C: Remember to use double backslashes (\\) in C string literals for paths.

4. Create Face Data Directory
The face_module.py will automatically create a face_data directory in the same location as your scripts if it doesn't exist. This is where captured face images will be stored.

Running the Application
Ensure all prerequisites are met and setup steps are completed.

Run the main GUI script:

python gui.py

The Secure File System GUI window will appear.

Usage
1. Registration
Enter a Username and Password.

Select a Role (user or admin) from the dropdown.

Click the "👤 Register" button.

The application will prompt you to capture your face using your webcam. Position your face clearly and press 's' to save the image. If face capture fails, registration will be aborted.

Upon successful face capture and database registration, you will receive a confirmation message.

2. Login
Enter your registered Username and Password.

Click the "🔓 Login" button.

The application will initiate face verification using your webcam. Look at the camera.

If face verification is successful along with correct credentials, you will be logged in.

A new "Secure File Operations" window will open based on your role.

3. Secure File Operations (User Role)
Once logged in as a user:

Create Secure File:

Click "Create Secure File".

Enter a desired filename (e.g., my_document). The system will automatically append .txt and prefix it with your username (e.g., yourusername_my_document.txt).

A new file will be created in your CUSTOM_FOLDER.

Read Secure File:

Click "Read Secure File".

Enter the filename (e.g., my_document).

A read-only editor will open displaying the file's content.

Write Secure File:

Click "Write Secure File".

Enter the filename (e.g., my_document).

An editor will open with the existing content (if any). You can modify or append text and click "Save File".

4. Admin Privileges
If logged in as an admin:

You will have all the "User Role" file operation buttons.

Admin File Access:

Click "Admin File Access".

This window allows you to list and view the content of all .txt files present in the CUSTOM_FOLDER, regardless of which user created them.

User Management:

Click "User Management".

This window displays a list of all registered users.

You can select a user and click "Delete User" to remove them from the database and delete their associated face data.

5. Theme Toggle
Click the "Dark Mode" / "Light Mode" button at the bottom of the main login window to switch themes.

Important Notes
Camera Access: Ensure your system grants camera access to the Python application.

MySQL Credentials: Remember to change the default MySQL user and password in database_setup.py to your actual credentials.

Secure Folder Path: Double-check that CUSTOM_FOLDER is identical in gui.py and secure_os_module.c.

Security: This project demonstrates concepts of biometric and database authentication for a file system. For a production-grade secure system, further security considerations (e.g., robust encryption for files, more advanced password hashing, secure communication, input validation beyond basic checks) would be necessary.

C Module Compilation: If you encounter issues with the C module, ensure your compiler is correctly set up and the compilation command is correct for your operating system.

Troubleshooting
"Error connecting to MySQL":

Ensure your MySQL server is running.

Verify the host, user, and password in database_setup.py are correct.

Check if the secure_file_system database was created by running python database_setup.py.

"Failed to open camera":

Ensure no other application is using your webcam.

Check your operating system's privacy settings to allow Python/applications to access the camera.

Try restarting your computer.

C Module not found/executable issues:

Ensure secure_os_module.c was compiled successfully and the executable (secure_os_module.exe or secure_os_module) is in the same directory as gui.py.

Verify the CUSTOM_FOLDER path is consistent across all files.

Face Recognition issues:

Ensure good lighting conditions.

Position your face clearly in the camera frame.

Try re-registering your face if issues persist.
