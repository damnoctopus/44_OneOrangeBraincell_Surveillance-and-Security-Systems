import tkinter as tk
from tkinter import messagebox, simpledialog
import passStoreFunc as fs
import func as fc
import tfa
import os
import customtkinter
from PIL import Image, ImageTk

factor_setup = False


def add_password():
    def save_password():
        website = website_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        if not (website and username and password):
            messagebox.showerror("Error", "All fields are required!")
            return

        strength_return = fc.check_strength(password)
        if strength_return is True:
            fs.generate_key()
            encrypted_password = fs.encrypt_data(password)
            # code to save the password details
            fs.save_password(website, username, encrypted_password)
            messagebox.showinfo("Success", f"Password for {website} has been added.")
            add_window.destroy()
        else:
            messagebox.showerror("Weak password", "Please enter a stronger password.")
            password_entry.delete(0, tk.END)

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
    global factor_setup

    if factor_setup is True:  # Check if 2FA is set up
        # Create a new top-level window for password retrieval
        retrieve_window = tk.Toplevel(root)
        retrieve_window.title("Retrieve Password")

        # Label and Entry widget to input website
        tk.Label(retrieve_window, text="Website:").grid(row=0, column=0, padx=10, pady=5)
        website_entry = tk.Entry(retrieve_window)
        website_entry.grid(row=0, column=1, padx=10, pady=5)

        # Function to fetch password
        def fetch_password():
            website = website_entry.get()  # Get the text entered in the Entry widget

            if not website:
                messagebox.showerror("Error", "Website is required!")
                return

            # Assuming fs.load_passwords() loads a list of passwords
            passwords = fs.load_passwords()
            found = False

            # Search for the password associated with the entered website
            for entry in passwords:
                if entry[0] == website:  # Compare with website
                    decrypted_password = fs.decrypt_data(entry[2].encode())  # Decrypt the password
                    messagebox.showinfo("Found", f"Username: {entry[1]}, Password: {decrypted_password}")
                    found = True
                    break

            if not found:
                messagebox.showerror("Error", "No password found for that website.")

        # Button to trigger password retrieval
        tk.Button(retrieve_window, text="Retrieve", command=fetch_password).grid(row=1, column=0, columnspan=2, pady=10)

    else:
        messagebox.showerror("Error", "Two-factor authentication is not set up.")


def setup_2fa():
    global factor_setup  # Access the global 2FA setup state

    if not factor_setup:
        # Ask the user if they want to set up 2FA
        confirm = messagebox.askyesno(
            "Set Up 2FA",
            "Two-factor authentication is not set up. Would you like to set it up now?"
        )
        if not confirm:
            return

        try:
            # Prompt user for their email
            user_email = simpledialog.askstring("Email", "Enter your email for 2FA setup:")
            if not user_email:
                messagebox.showerror("Error", "Email is required to set up 2FA.")
                return

            # Check or store the user email
            file_path = "fileData/user.txt"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    stored_email = file.read().strip()
                if user_email != stored_email:
                    messagebox.showerror("Error", "Email does not match the stored user.")
                    return
            else:
                # Store the email if not already present
                with open(file_path, "w") as file:
                    file.write(user_email)

            # Generate secret and QR code
            secret = tfa.generate_2fa_secret(user_email)
            file_path2 = f"fileData/{user_email}_2fa_qr.png"
            os.makedirs(os.path.dirname(file_path2), exist_ok=True)
            if not os.path.exists(file_path2):
                qr_file = tfa.generate_qr_code(secret, user_email)

                # Display QR code to the user
                qr_window = tk.Toplevel()
                qr_window.title("Scan QR Code")
                qr_label = tk.Label(qr_window, text="Scan this QR code with your authenticator app:")
                qr_label.pack(pady=10)

                qr_image = Image.open(qr_file)
                qr_photo = ImageTk.PhotoImage(qr_image)
                qr_canvas = tk.Label(qr_window, image=qr_photo)
                qr_canvas.image = qr_photo  # Keep a reference to avoid garbage collection
                qr_canvas.pack(pady=10)

            # OTP validation
            for i in range(3):
                user_otp = simpledialog.askstring("OTP", "Enter the OTP from your authenticator app:")
                if tfa.validate_otp(secret, user_otp):
                    messagebox.showinfo("Success", "Successfully authenticated.")
                    factor_setup = True  # Update the global variable
                    qr_window.destroy()
                    return
                else:
                    messagebox.showerror("Error", f"Invalid OTP. Attempt {i+1}/3.")

            messagebox.showerror("Error", "Failed to validate OTP after 3 attempts.")
            qr_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while setting up 2FA:\n{str(e)}")
    else:
        messagebox.showinfo("Info", "Two-factor authentication is already set up.")


def reset_2fa():
    confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset 2FA?")
    if confirm:
        try:
            fs.reset2fa()  # Call the reset2fa function
            messagebox.showinfo("Success", "2FA has been reset successfully.")
            global factor_setup
            factor_setup = False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while resetting 2FA:\n{str(e)}")
    else:
        messagebox.showinfo("Cancelled", "2FA reset was cancelled.")


def generate_strong_password():

    strong_pass = fc.Genstrongpass()
    # print to console
    print(strong_pass)
    # Display the password in a message box
    messagebox.showinfo("Generated Password", f"Your strong password is:\n{strong_pass}")


def quit_app():
    root.quit()

# Main body


if not os.path.exists('fileData/secret.key'):
    fs.generate_key()
factor_setup = False


# Main Window
root = customtkinter.CTk()
root.title("Password Manager Menu")
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


customtkinter.CTkLabel(root, text="Welcome to PassManager", font=("Arial", 16)).pack(pady=10)

customtkinter.CTkButton(root, text="1. Add Password", command=add_password, width=30).pack(pady=5)
customtkinter.CTkButton(root, text="2. Retrieve Password", command=retrieve_password, width=30).pack(pady=5)
customtkinter.CTkButton(root, text="3. Setup 2FA", command=setup_2fa, width=30).pack(pady=5)
customtkinter.CTkButton(root, text="4. Reset 2FA", command=reset_2fa, width=30).pack(pady=5)
customtkinter.CTkButton(root, text="5. Generate Strong Password", command=generate_strong_password, width=30).pack(pady=5)
customtkinter.CTkButton(root, text="6. Quit", command=quit_app, width=30).pack(pady=5)

root.mainloop()