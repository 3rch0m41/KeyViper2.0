from cryptography.fernet import Fernet
def KeyGen (): 
    key = Fernet.generate_key()
    file = open("encryption_key.txt", 'wb')
    file.write(key)
    file.close()
    return key
