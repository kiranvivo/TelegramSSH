"""Functions for securely retrieving/storing a token from/to a file using a password.

@author Weston Cook
"""


from crypto_tools import getSalt, getKeyFromPassword, Fernet, \
     validateFernet, encrypt, decrypt, InvalidToken
import getpass


def newPassword(prompt='Password: '):
    """Securely obtain a new password from the user."""
    while True:
        p = getpass.getpass(prompt)
        if p == getpass.getpass('Confirm password: '):
            return p
        else:
            print('Passwords do not match. Try again.')


def getToken(salt_path, telegram_token_path, password=None):
    """Get the decrypted token from a file or from the user."""
    # Get password salt
    salt = getSalt(salt_path)

    # Get the Telegram token if it exists,
    # otherwise get it from the user, encrypt it, and save it
    try:
        with open(telegram_token_path, 'rb') as f:
            # Read the encrypted token
            telegram_token_encrypted = f.readline()

            # Note that the token has not been decrypted yet
            telegram_token = None
    except FileNotFoundError:
        # Get the token from the user
        telegram_token = input('Enter Telegram Bot token: ')
        # Encrypt and save the token

        # Get encryption password
        if password is None:
            password = newPassword('Enter a password to encrypt the token: ')

        # Get fernet
        key = getKeyFromPassword(salt, password)
        fernet = Fernet(key)

        # Encrypt the Telegram token
        telegram_token_encrypted = encrypt(telegram_token, fernet)

        # Save the encrypted Telegram token
        with open(telegram_token_path, 'wb+') as f:
            f.write(telegram_token_encrypted)

    # Decrypt the token if necessary
    if telegram_token is None:
        fails = 0
        while fails < 3:
            # Get encryption password
            if password is None:
                password = newPassword('Enter a password to encrypt the token: ')

            # Get fernet
            key = getKeyFromPassword(salt, password)
            fernet = Fernet(key)

            # Decrypt the Telegram token
            try:
                telegram_token = decrypt(telegram_token_encrypted, fernet)
                break
            except InvalidToken:
                telegram_token = None
                fails += 1
                print('Invalid password.')

        if telegram_token is None:  # User exceeded maximum password attempts
            print('Maximum password attempts exceeded. Exiting.')
            exit()

    return telegram_token
