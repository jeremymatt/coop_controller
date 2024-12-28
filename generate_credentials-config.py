import hashlib
import os

run = True
while run:
    username = input("Enter username:")
    password = input("Enter password:")

    good_entry = input("You entered:\n  Username: {}\n  Password: {}\nIs this correct? (y/n)".format(username,password))

    if good_entry.lower() == 'y':
        user_hash = hashlib.md5(username.encode()).hexdigest()
        pass_hash = hashlib.md5(password.encode()).hexdigest()
        run = False
        write_config = True
        if os.path.isfile('credentials.config'):
            overwrite = input("Found existing credentials.config file.  Overwrite? (y/n)")
            if overwrite.lower() != 'y':
                write_config = False
                print("Exiting")
        if write_config:
            with open('credentials.config','w') as f:
                f.write('{}\n'.format(user_hash))
                f.write('{}'.format(pass_hash))

