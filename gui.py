from face_module import capture_face, verify_face
from database_setup import (
    register_user_to_db, 
    verify_user_credentials, 
    update_last_login, 
    log_login_attempt,
    create_database_connection,
    delete_user_from_db  # <-- FIX 2: Import delete_user_from_db
)
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import os
import subprocess
import platform

# Define the same custom folder path as in C code
CUSTOM_FOLDER = r"C:\Users\DELL\Desktop\secure folder"  # Change this to match your C code
VALID_ROLES = {"admin", "user"}

def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist - same as C function"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Directory '{path}' created.")
        except Exception as e:
            print(f"Error creating directory: {e}")

def register_user():
    username = username_input.get().strip()
    password = password_input.get().strip()
    role = role_var.get().strip().lower()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return
    
    if ':' in username or len(username) < 3:
        messagebox.showwarning("Input Error", "Username must be at least 3 characters and cannot contain ':'")
        return
    
    if len(password) < 4:
        messagebox.showwarning("Input Error", "Password must be at least 4 characters long.")
        return

    if role not in VALID_ROLES:
        messagebox.showwarning("Input Error", "Invalid role selection.")
        return

    # Check if user already exists in database
    connection = create_database_connection()
    if not connection:
        messagebox.showerror("Database Error", "Could not connect to database.")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showwarning("Registration Error", "User already exists.")
            return
    except Exception as e:
        messagebox.showerror("Database Error", f"Error checking user: {e}")
        return
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    # Face capture step
    messagebox.showinfo("Face Registration", 
                       "We will now capture your face for biometric authentication.\n\n" +
                       "Instructions:\n" +
                       "1. Position your face clearly in the camera frame\n" +
                       "2. Press 's' to save your face image\n" +
                       "3. Press 'q' to cancel")
    
    if not capture_face(username):
        messagebox.showerror("Face Capture Failed", "Face capture failed. Registration aborted.")
        return

    # Register user in database
    face_image_path = os.path.join("face_data", f"{username}.jpg")
    if register_user_to_db(username, password, role, face_image_path):
        messagebox.showinfo("Registration Successful", 
                           f"User '{username}' registered successfully!\n" +
                           f"Role: {role}\n" +
                           "You can now login with your credentials and face verification.")
        # Clear input fields after successful registration
        username_input.delete(0, tk.END)
        password_input.delete(0, tk.END)
        role_var.set("user")
    else:
        messagebox.showerror("Registration Failed", "Failed to register user in database.")

def login_user():
    username = username_input.get().strip()
    password = password_input.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    # Verify credentials against database
    user = verify_user_credentials(username, password)
    if user:
        face_image_path = user['face_image_path']
        # Use face_image_path for verification
    else:
        log_login_attempt(username, success=False)
        messagebox.showwarning("Login Error", "Invalid username or password.")
        return

    # Face verification step
    messagebox.showinfo("Face Verification", 
                       "Please verify your identity with face recognition.\n\n" +
                       "Instructions:\n" +
                       "1. Look directly at the camera\n" +
                       "2. Keep your face well-lit and clearly visible\n" +
                       "3. Stay still during verification\n" +
                       "4. Press 'q' to cancel if needed")
    
    if not verify_face(username):
        log_login_attempt(username, success=False)
        messagebox.showerror("Authentication Failed", 
                           "Face verification failed. Access denied.\n\n" +
                           "Please ensure:\n" +
                           "• Your face is clearly visible\n" +
                           "• Lighting is adequate\n" +
                           "• You are the registered user")
        return

    # Successful login
    log_login_attempt(username, success=True)
    update_last_login(username)
    
    messagebox.showinfo("Login Successful", 
                       f"Welcome {username}!\n" +
                       f"Role: {user['role']}\n" +
                       "Face verification completed successfully.")
    
    # Clear input fields
    username_input.delete(0, tk.END)
    password_input.delete(0, tk.END)
    
    # Open secure file window
    open_secure_file_window(username, user['role'])

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode

    style = ttk.Style()
    if dark_mode:
        root.configure(bg="#1e1e1e")
        title.config(bg="#1e1e1e", fg="#f2f2f2")
        subtitle.config(bg="#1e1e1e", fg="#cfcfcf")
        login_frame.config(bg="#2e2e2e")
        form_frame.config(bg="#2e2e2e")
        username_label.config(bg="#2e2e2e", fg="white")
        password_label.config(bg="#2e2e2e", fg="white")
        role_label.config(bg="#2e2e2e", fg="white")
        username_input.config(bg="#3a3a3a", fg="white", insertbackground="white")
        password_input.config(bg="#3a3a3a", fg="white", insertbackground="white")
        button_frame.config(bg="#2e2e2e")
        login_btn.config(bg="#388e3c", fg="white", activebackground="#2e7d32")
        register_btn.config(bg="#1976d2", fg="white", activebackground="#1565c0")
        toggle_button.config(bg="#444", fg="white", activebackground="#555", text="Light Mode")
        status_frame.config(bg="#1e1e1e")
        status_label.config(bg="#1e1e1e", fg="#bbb")

        # Style ttk.Combobox for dark mode
        style.theme_use('default')
        style.configure("TCombobox",
                        fieldbackground="#3a3a3a",
                        background="#3a3a3a",
                        foreground="white",
                        selectforeground="white",
                        selectbackground="#3a3a3a")
        role_dropdown.configure(style="TCombobox")
    else:
        root.configure(bg="#d0ecff")
        title.config(bg="#d0ecff", fg="#333")
        subtitle.config(bg="#d0ecff", fg="#444")
        login_frame.config(bg="white")
        form_frame.config(bg="white")
        username_label.config(bg="white", fg="black")
        password_label.config(bg="white", fg="black")
        role_label.config(bg="white", fg="black")
        username_input.config(bg="white", fg="black", insertbackground="black")
        password_input.config(bg="white", fg="black", insertbackground="black")
        button_frame.config(bg="white")
        login_btn.config(bg="#4CAF50", fg="white", activebackground="#388e3c")
        register_btn.config(bg="#2196F3", fg="white", activebackground="#1976d2")
        toggle_button.config(bg="white", fg="#333", activebackground="#ddd", text="Dark Mode")
        status_frame.config(bg="#d0ecff")
        status_label.config(bg="#d0ecff", fg="gray")

        # Style ttk.Combobox for light mode
        style.theme_use('default')
        style.configure("TCombobox",
                        fieldbackground="white",
                        background="white",
                        foreground="black",
                        selectforeground="black",
                        selectbackground="white")
        role_dropdown.configure(style="TCombobox")
        
def list_files(directory=CUSTOM_FOLDER):
    """List all text files in the custom folder directory"""
    files = []
    try:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(".txt"):
                    files.append(file)
        else:
            create_directory_if_not_exists(directory)
    except Exception as e:
        print(f"Error listing files: {e}")
    return files

def get_full_path(filename):
    """Get full path for file in custom folder"""
    return os.path.join(CUSTOM_FOLDER, filename)

def open_secure_file_window(username, role):
    sf_window = tk.Toplevel(root)
    sf_window.title(f"Secure File Operations - {username} ({role})")
    sf_window.geometry("500x520")
    sf_window.resizable(False, False)
    sf_window.configure(bg="white")

    # Title
    header_label = tk.Label(sf_window, text=f"Welcome {username}!", font=("Segoe UI", 14, "bold"), bg="white")
    header_label.pack(pady=(15, 5))
    
    role_label = tk.Label(sf_window, text=f"Role: {role}", font=("Segoe UI", 10), bg="white")
    role_label.pack(pady=(0, 5))
    
    # Database status
    connection = create_database_connection()
    if connection:
        status_text = "🟢 Database Connected"
        connection.close()
    else:
        status_text = "🔴 Database Disconnected"
    
    db_status_label = tk.Label(sf_window, text=status_text, font=("Segoe UI", 9), bg="white", fg="gray")
    db_status_label.pack(pady=(0, 10))

    # Frame for file actions
    actions_frame = tk.Frame(sf_window, bg="white")
    actions_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Create File Button
    create_btn = tk.Button(actions_frame, text="Create Secure File", font=("Segoe UI", 11),
                           bg="#6a5acd", fg="white", width=22, 
                           command=lambda: show_file_dialog("create", username))
    create_btn.pack(pady=12)

    # Read File Button
    read_btn = tk.Button(actions_frame, text="Read Secure File", font=("Segoe UI", 11),
                         bg="#008080", fg="white", width=22, 
                         command=lambda: show_file_dialog("read", username))
    read_btn.pack(pady=12)

    # Write File Button
    write_btn = tk.Button(actions_frame, text="Write Secure File", font=("Segoe UI", 11),
                          bg="#ff8c00", fg="white", width=22, 
                          command=lambda: show_file_dialog("write", username))
    write_btn.pack(pady=12)
    
    # Admin-only feature: Access all files
    if role == "admin":
        admin_btn = tk.Button(actions_frame, text="Admin File Access", font=("Segoe UI", 11),
                             bg="#f44336", fg="white", width=22, 
                             command=lambda: admin_file_access(username))
        admin_btn.pack(pady=12)
        
        # Admin: User Management
        user_mgmt_btn = tk.Button(actions_frame, text="User Management", font=("Segoe UI", 11),
                                 bg="#9c27b0", fg="white", width=22, 
                                 command=lambda: open_user_management())
        user_mgmt_btn.pack(pady=12)

def open_user_management():
    """Admin-only user management window"""
    mgmt_window = tk.Toplevel(root)
    mgmt_window.title("User Management")
    mgmt_window.geometry("700x600")
    mgmt_window.configure(bg="white")
    
    header = tk.Label(mgmt_window, text="User Management", font=("Segoe UI", 14, "bold"), bg="white")
    header.pack(pady=(15,10))
    
    # Create notebook with tabs
    notebook = ttk.Notebook(mgmt_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tab 1: View Users
    tab1 = tk.Frame(notebook, bg="white")
    notebook.add(tab1, text="View Users")
    
    # Users Listbox
    users_frame = tk.Frame(tab1, bg="white")
    users_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    users_listbox = tk.Listbox(users_frame, font=("Segoe UI", 10), width=50, height=15)
    users_listbox.pack(side=tk.LEFT, fill="both", expand=True)
    
    users_scrollbar = tk.Scrollbar(users_frame)
    users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    users_listbox.config(yscrollcommand=users_scrollbar.set)
    users_scrollbar.config(command=users_listbox.yview)
    
    def delete_selected_user():  # <-- FIX 1: Proper indentation
        selection = users_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return
        
        user_info = users_listbox.get(selection[0])
        username = user_info.split(' ')[0]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?")
        if not confirm:
            return

        if delete_user_from_db(username):
            from face_module import delete_face_data
            delete_face_data(username)
            messagebox.showinfo("Deleted", f"User '{username}' deleted successfully!")
            refresh_users()
        else:
            messagebox.showerror("Error", f"Failed to delete user '{username}'.")

    def refresh_users():
        users_listbox.delete(0, tk.END)
        connection = create_database_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT username, role, created_at, last_login FROM users ORDER BY created_at")
                users = cursor.fetchall()
                for user in users:
                    user_info = f"{user[0]} ({user[1]}) - Created: {user[2]} - Last Login: {user[3] or 'Never'}"
                    users_listbox.insert(tk.END, user_info)
            except Exception as e:
                messagebox.showerror("Database Error", f"Error fetching users: {e}")
            finally:
                cursor.close()
                connection.close()
    
    # Initial load
    refresh_users()
    
    users_btn_frame = tk.Frame(tab1, bg="white")
    users_btn_frame.pack(fill="x", pady=10)
    
    refresh_users_btn = tk.Button(users_btn_frame, text="Refresh", command=refresh_users, 
                                 font=("Segoe UI", 10), bg="#2196F3", fg="white")
    refresh_users_btn.pack(side=tk.LEFT, padx=10)

    delete_user_btn = tk.Button(users_btn_frame, text="Delete User", command=delete_selected_user,
                               font=("Segoe UI", 10), bg="#f44336", fg="white")
    delete_user_btn.pack(side=tk.LEFT, padx=10)  # <-- FIX 3: Proper indentation


def show_file_dialog(action, username):
    """Show dialog to get filename for file operations"""
    dialog = tk.Toplevel(root)
    dialog.title(f"{action.capitalize()} File")
    dialog.geometry("400x180")
    dialog.configure(bg="white")
    dialog.resizable(False, False)

    label = tk.Label(dialog, text=f"Enter file name for {action}:", font=("Segoe UI", 11), bg="white")
    label.pack(pady=(20, 10))
    
    entry = tk.Entry(dialog, font=("Segoe UI", 11), width=25, relief="solid")
    entry.pack(pady=(0, 15))
    entry.focus()
    
    def proceed():
        filename = entry.get().strip()
        if not filename:
            messagebox.showwarning("Input Error", "Please enter a file name.")
            return
            
        dialog.destroy()
        
        if action == "create":
            create_secure_file(filename, username)
        elif action == "read":
            open_file_editor(filename, "read", username)
        elif action == "write":
            open_file_editor(filename, "write", username)
    
    entry.bind('<Return>', lambda event: proceed())
    
    proceed_btn = tk.Button(dialog, text="Proceed", font=("Segoe UI", 10), 
                          bg="#2196F3", fg="white", width=12, command=proceed)
    proceed_btn.pack(pady=10)

def create_secure_file(filename, username):
    """Create a new secure file"""
    create_directory_if_not_exists(CUSTOM_FOLDER)
    
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    
    user_filename = f"{username}_{filename}"
    full_path = get_full_path(user_filename)
    
    if os.path.exists(full_path):
        messagebox.showwarning("File Exists", f"File '{user_filename}' already exists!")
        return
    
    try:
        with open(full_path, 'w') as f:
            f.write(f"# Secure File created by {username}\n")
            f.write(f"# Created on: {os.popen('date /t').read().strip()}\n\n")
            f.write("Your secure content goes here...\n")
        
        messagebox.showinfo("File Created", f"Secure file '{user_filename}' created successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create file: {e}")

def open_file_editor(filename, mode, username):
    """Open file editor for read/write operations"""
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    
    user_filename = f"{username}_{filename}"
    full_path = get_full_path(user_filename)
    
    if mode == "read" and not os.path.exists(full_path):
        messagebox.showwarning("File Not Found", f"File '{user_filename}' not found!")
        return
    
    editor_window = tk.Toplevel(root)
    editor_window.title(f"{mode.capitalize()} File: {user_filename}")
    editor_window.geometry("700x500")
    editor_window.configure(bg="white")
    
    # Header
    header_frame = tk.Frame(editor_window, bg="white")
    header_frame.pack(fill="x", padx=10, pady=5)
    
    title_label = tk.Label(header_frame, text=f"File: {user_filename}", 
                          font=("Segoe UI", 12, "bold"), bg="white")
    title_label.pack(side=tk.LEFT)
    
    mode_label = tk.Label(header_frame, text=f"Mode: {mode.upper()}", 
                         font=("Segoe UI", 10), bg="white", fg="gray")
    mode_label.pack(side=tk.RIGHT)
    
    # Text editor
    text_frame = tk.Frame(editor_window)
    text_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    text_editor = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 11))
    text_editor.pack(fill="both", expand=True)
    
    # Load existing content if reading
    if mode == "read" and os.path.exists(full_path):
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                text_editor.insert(tk.END, content)
            text_editor.config(state=tk.DISABLED)  # Make read-only
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return
    
    # Button frame
    button_frame = tk.Frame(editor_window, bg="white")
    button_frame.pack(fill="x", padx=10, pady=5)
    
    if mode == "write":
        def save_file():
            try:
                content = text_editor.get(1.0, tk.END)
                with open(full_path, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"File '{user_filename}' saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        
        save_btn = tk.Button(button_frame, text="Save File", font=("Segoe UI", 10),
                           bg="#4CAF50", fg="white", command=save_file)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Load existing content for editing
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    text_editor.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    close_btn = tk.Button(button_frame, text="Close", font=("Segoe UI", 10),
                         bg="#f44336", fg="white", command=editor_window.destroy)
    close_btn.pack(side=tk.RIGHT, padx=5)

def admin_file_access(username):
    """Admin can access all files in the system"""
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin File Access")
    admin_window.geometry("600x400")
    admin_window.configure(bg="white")
    
    header = tk.Label(admin_window, text="Admin File Access", font=("Segoe UI", 14, "bold"), bg="white")
    header.pack(pady=10)
    
    # File list frame
    list_frame = tk.Frame(admin_window, bg="white")
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    files_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), height=15)
    files_listbox.pack(side=tk.LEFT, fill="both", expand=True)
    
    files_scrollbar = tk.Scrollbar(list_frame)
    files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    files_listbox.config(yscrollcommand=files_scrollbar.set)
    files_scrollbar.config(command=files_listbox.yview)
    
    def refresh_files():
        files_listbox.delete(0, tk.END)
        files = list_files()
        for file in files:
            files_listbox.insert(tk.END, file)
    
    def open_selected_file():
        selection = files_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to open.")
            return
        
        filename = files_listbox.get(selection[0])
        full_path = get_full_path(filename)
        
        # Open in read mode for admin
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            view_window = tk.Toplevel(admin_window)
            view_window.title(f"Admin View: {filename}")
            view_window.geometry("600x400")
            
            text_area = scrolledtext.ScrolledText(view_window, wrap=tk.WORD, font=("Consolas", 10))
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
    
    # Initial load
    refresh_files()
    
    # Buttons
    btn_frame = tk.Frame(admin_window, bg="white")
    btn_frame.pack(fill="x", pady=10)
    
    refresh_btn = tk.Button(btn_frame, text="Refresh", command=refresh_files,
                           font=("Segoe UI", 10), bg="#2196F3", fg="white")
    refresh_btn.pack(side=tk.LEFT, padx=20)
    
    open_btn = tk.Button(btn_frame, text="Open Selected", command=open_selected_file,
                        font=("Segoe UI", 10), bg="#4CAF50", fg="white")
    open_btn.pack(side=tk.LEFT, padx=10)

# Main GUI Setup
root = tk.Tk()
root.title("Secure File System - Biometric Authentication")
root.geometry("450x600")
root.resizable(False, False)

# Theme variable
dark_mode = False
root.configure(bg="#d0ecff")

# Title
title = tk.Label(root, text="🔐 Secure File System", font=("Segoe UI", 20, "bold"), 
                bg="#d0ecff", fg="#333")
title.pack(pady=(30, 10))

subtitle = tk.Label(root, text="Biometric + Database Authentication", font=("Segoe UI", 11), 
                   bg="#d0ecff", fg="#444")
subtitle.pack(pady=(0, 30))

# Login Frame
login_frame = tk.Frame(root, bg="white", relief="raised", bd=2)
login_frame.pack(pady=20, padx=40, fill="both", expand=True)

# Form elements
form_frame = tk.Frame(login_frame, bg="white")
form_frame.pack(pady=30, padx=30, fill="both", expand=True)

# Username
username_label = tk.Label(form_frame, text="Username:", font=("Segoe UI", 11), bg="white")
username_label.pack(anchor="w", pady=(0, 5))

username_input = tk.Entry(form_frame, font=("Segoe UI", 11), width=25, relief="solid")
username_input.pack(pady=(0, 15), ipady=5)

# Password
password_label = tk.Label(form_frame, text="Password:", font=("Segoe UI", 11), bg="white")
password_label.pack(anchor="w", pady=(0, 5))

password_input = tk.Entry(form_frame, font=("Segoe UI", 11), width=25, show="*", relief="solid")
password_input.pack(pady=(0, 15), ipady=5)

# Role (for registration)
role_label = tk.Label(form_frame, text="Role (for registration):", font=("Segoe UI", 11), bg="white")
role_label.pack(anchor="w", pady=(0, 5))

role_var = tk.StringVar(value="user")
role_dropdown = ttk.Combobox(form_frame, textvariable=role_var, values=["user", "admin"], 
                            state="readonly", font=("Segoe UI", 11), width=22)
role_dropdown.pack(pady=(0, 20))

# Buttons
button_frame = tk.Frame(login_frame, bg="white")
button_frame.pack(pady=(0, 30), padx=30, fill="x")

login_btn = tk.Button(button_frame, text="🔓 Login", font=("Segoe UI", 11, "bold"), 
                     bg="#4CAF50", fg="white", width=15, pady=8, command=login_user)
login_btn.pack(side=tk.LEFT, padx=(0, 10))

register_btn = tk.Button(button_frame, text="👤 Register", font=("Segoe UI", 11, "bold"), 
                        bg="#2196F3", fg="white", width=15, pady=8, command=register_user)
register_btn.pack(side=tk.RIGHT, padx=(10, 0))

# Theme toggle
toggle_button = tk.Button(root, text="Dark Mode", font=("Segoe UI", 9), 
                         bg="white", fg="#333", command=toggle_theme)
toggle_button.pack(pady=10)

# Status bar
status_frame = tk.Frame(root, bg="#d0ecff")
status_frame.pack(fill="x", side="bottom")

status_label = tk.Label(status_frame, text="Ready - Please login or register", 
                       font=("Segoe UI", 9), bg="#d0ecff", fg="gray")
status_label.pack(pady=5)

# Keyboard shortcuts
def on_enter(event):
    login_user()

root.bind('<Return>', on_enter)
username_input.bind('<Return>', lambda e: password_input.focus())
password_input.bind('<Return>', on_enter)

if __name__ == "__main__":
    # Ensure required directories exist
    create_directory_if_not_exists(CUSTOM_FOLDER)
    
    # Start the GUI
    root.mainloop()
