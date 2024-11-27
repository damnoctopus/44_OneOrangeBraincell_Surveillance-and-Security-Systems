import passStoreFunc as fs
import tfa
import os
import func as fc
import shutil


def main():
        if not os.path.exists('fileData/secret.key'):
            fs.generate_key()
        factor_setup = False

        while True:
            choice = int(input("Would you like to\n 1.Add\n 2.Retrieve\n 3.Setup 2FA \n 4.Reset 2FA \n "
                               "5.Generate strong password \n 6.Quit \n"))

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
                if factor_setup is True:
                    website = input("Enter the website to retrieve: ")
                    factor_verify = tfa.two_factor_auth()
                    if factor_verify:
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
                        print("Failed to verify user")

                else:
                    print("Two Factor Authentication not setup")

            elif choice == 3:
                if factor_setup is False:
                    factor_setup = tfa.two_factor_auth()
                    print("Two factor authentication has been setup")
                else:
                    print("Two factor authentication has already been setup if you wish to reset your 2FA please choose"
                          " option 4")
            elif choice == 4:
                resop=input("Do you want to reset y/n").lower()
                if resop=="y":
                    shutil.rmtree('fileData')
                elif resop=="n":
                    print("Reset has been cancelled")
                else:
                    print("Invalid option")

            elif choice == 5:
                Suggestions=fc.Genstrongpass()
                print(f"Strong Password: {Suggestions}")

            elif choice == 6:
                break

            else:
                print("Invalid option. Please choose a valid option.")


main()
