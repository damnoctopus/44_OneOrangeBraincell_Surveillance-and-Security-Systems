import passStoreFunc as fs
import os
import func as fc

def main():
        factorauth = True
        if not os.path.exists('fileData/secret.key'):
            fs.generate_key()

        while True:
            choice = int(input("Would you like to\n 1.Add\n 2.Retrieve\n 3.Setup 2FA \n 4.Quit \n"))

            if choice == 1:
                # code add a new password
                website = input("Enter the website: ")
                username = input("Enter the username: ")
                while True:
                    password = input("Enter the password: ")
                    strenghtreturn = fc.check_strength(password)
                    if (strenghtreturn is True):
                        encrypted_password = fs.encrypt_data(password)
                        # code to save the password details
                        fs.save_password(website, username, encrypted_password)
                        print(f"Password for {website} has been added.")
                        break
                    else:
                        print(f"The password is weak.")
                        print("Try a new password")


            elif choice == 2:
                # retrieve a password
                if factorauth is True:
                    website = input("Enter the website to retrieve: ")
                    passwords = fs.load_passwords()
                    found = False

                    for entry in passwords:
                        if entry[0] == website:
                            decrypted_password = fs.decrypt_data(entry[2].encode())
                            print(f"Username: {entry[1]}, Password: {decrypted_password}")
                            found = True
                            break

                    if not found:
                        print("No password found for that website.")

                else:
                    print("2Factor Authentication not passed ")

            elif choice == 3:
                print("hehe")
            elif choice == 4:
                break

            else:
                print("Invalid option. Please choose 1,2,3 or 4")


main()
