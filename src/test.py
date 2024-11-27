import tkinter as tk
from tkinter import messagebox
import passStoreFunc as fs
import func as fc
import os
import string

def add_password():
    def save_password():
        website = website_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        if not (website and username and password):
            messagebox.showerror("Error", "All fields are required!")
            return

        if fc.check_strength(password):
            encrypted_password = fs.encrypt_data(password)
            fs.save_password(website, username, encrypted_password)
            messagebox.showinfo("Success", f"Password for {website} has been added.")
            add_window.destroy()
        else:
            messagebox.showwarning("Weak Password", "The password is weak. Please try again.")

    add_window = tk.Toplevel(root)
    add_window.title("Add Password")

    tk.Label(add_window, text="Website:").grid(row=0, column=0, padx=10, pady=5)
    website_entry = tk.Entry(add_window)
    website_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Username:").grid(row=1, column=0, padx=10, pady=5)
    username_entry = tk.Entry(add_window)
    username_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Password:").grid(row=2, column=0, padx=10, pady=5)
    password_entry = tk.Entry(add_window, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Button(add_window, text="Save", command=save_password).grid(row=3, column=0, columnspan=2, pady=10)

def retrieve_password():
    def fetch_password():
        website = website_entry.get()

        if not website:
            messagebox.showerror("Error", "Website is required!")
            return

        passwords = fs.load_passwords()
        for entry in passwords:
            if entry[0] == website:
                decrypted_password = fs.decrypt_data(entry[2].encode())
                messagebox.showinfo("Password Found", f"Username: {entry[1]}\nPassword: {decrypted_password}")
                retrieve_window.destroy()
                return

        messagebox.showwarning("Not Found", "No password found for that website.")

    retrieve_window = tk.Toplevel(root)
    retrieve_window.title("Retrieve Password")

    tk.Label(retrieve_window, text="Website:").grid(row=0, column=0, padx=10, pady=5)
    website_entry = tk.Entry(retrieve_window)
    website_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(retrieve_window, text="Retrieve", command=fetch_password).grid(row=1, column=0, columnspan=2, pady=10)

def setup_2fa():
    # Add functionality to setup 2FA here
    messagebox.showinfo("Setup 2FA", "Setup 2FA functionality placeholder.")

def reset_2fa():
    confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset 2FA?")
    if confirm:
        try:
            fs.reset2fa()  # Call the reset2fa function
            messagebox.showinfo("Success", "2FA has been reset successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while resetting 2FA:\n{str(e)}")
    else:
        messagebox.showinfo("Cancelled", "2FA reset was cancelled.")

def generate_strong_password():

    strong_pass = fc.Genstrongpass()
    #print to console
    print(strong_pass)
    # Display the password in a message box
    messagebox.showinfo("Generated Password", f"Your strong password is:\n{strong_pass}")



def quit_app():
    root.quit()

# Main Window
root = tk.Tk()
root.title("PassStore Menu")

tk.Label(root, text="Welcome to PassStore", font=("Arial", 16)).pack(pady=10)

tk.Button(root, text="1. Add Password", command=add_password, width=30).pack(pady=5)
tk.Button(root, text="2. Retrieve Password", command=retrieve_password, width=30).pack(pady=5)
tk.Button(root, text="3. Setup 2FA", command=setup_2fa, width=30).pack(pady=5)
tk.Button(root, text="4. Reset 2FA", command=reset_2fa, width=30).pack(pady=5)
tk.Button(root, text="5. Generate Strong Password", command=generate_strong_password, width=30).pack(pady=5)
tk.Button(root, text="6. Quit", command=quit_app, width=30).pack(pady=5)

root.mainloop()
