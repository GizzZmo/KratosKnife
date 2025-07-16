from Crypto import Random
from Crypto.Cipher import AES
import os
import hashlib
import requests # Added requests for potential C2 communication from brute-forced client if needed
import sys # Added sys for exit functionality

class Encryptor:
    def __init__(self, key, file_name):
        self.plainkey = key
        self.key = hashlib.sha256(key.encode('utf-8')).digest()
        self.file_name = file_name

    def pad(self, s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key, key_size=256):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)
        
    def encrypt_file(self):
        with open(self.file_name, 'rb') as f:
            plaintext = f.read()
        enc = self.encrypt(plaintext, self.key)
        with open(self.file_name, 'w') as f:
            f.write("from Crypto import Random\n")
            f.write("from Crypto.Cipher import AES\n")
            f.write("import hashlib\n")
            f.write("import sys\n")
            f.write("import requests\n")
            
            f.write("\nclass Decryptor:\n")
            f.write("\tdef __init__(self, key):\n") # Removed file_name parameter
            f.write("\t\tself.key = hashlib.sha256(key.encode('utf-8')).digest()\n\n")
            
            f.write("\tdef pad(self, s):\n")
            f.write("\t\treturn s + b\"\\0\" * (AES.block_size - len(s) % AES.block_size)\n\n")
            
            f.write("\tdef decrypt(self, ciphertext): # Takes ciphertext directly\n")
            f.write("\t\tiv = ciphertext[:AES.block_size]\n")
            f.write("\t\tcipher = AES.new(self.key, AES.MODE_CBC, iv)\n") # Use self.key
            f.write("\t\tplaintext = cipher.decrypt(ciphertext[AES.block_size:])\n")
            f.write("\t\treturn plaintext.rstrip(b\"\\0\")\n\n")
            
            f.write("class BruteForce:\n")
            f.write("\tdef start(encrypted_codes): \n") # Made static method, takes encrypted_codes
            f.write("\t\tpassword = 0 # Initialize password locally\n")
            f.write("\t\twhile True:\n")
            f.write("\t\t\ttry:\n")
            f.write("\t\t\t\ttest = Decryptor(str(password)) # Pass password only\n")
            f.write("\t\t\t\tdecrypted_code = test.decrypt(encrypted_codes) \n") # Pass encrypted_codes directly
            f.write("\t\t\t\texecutable = decrypted_code.decode('utf-8') \n") # Specify encoding
            f.write("\t\t\t\treturn executable \n")
            f.write("\t\t\texcept (UnicodeDecodeError, ValueError, IndexError): # Catch common decryption errors\n")
            f.write("\t\t\t\tpassword += 1\n")
            f.write("\t\t\t\tif password > 99999: # Add a practical limit for brute-force to avoid infinite loop\n")
            f.write("\t\t\t\t\tsys.exit(\"Brute-force failed to find correct key within range.\")\n\n")
            
            f.write(f"encrypted_codes = {enc}\n")
            f.write(f"executable = BruteForce.start(encrypted_codes)\n") # Call as static method with encrypted_codes
            f.write("exec(executable)\n")      


if __name__ == '__main__':
    notice = """
    Cracking Speed on RunTime
    =========================
    With 2 GB RAM & 1 GHz Proceessor 
    --------------------------------    
    Guess Speed: 2000 Numeric Pass/ Seconds

    Password Like : 10000 is cracked in 5 seconds
    So Delay Time In Program Will be 5 seconds
    
    """
    print(notice)

    key = input("[?] Enter Numeric Key : ")
    path = input("[?] Enter Path of File : ")

    print("\n[*] Initiating Encryption Process ...")
    test = Encryptor(key, path) 
    test.encrypt_file()
    print("[+] Process Completed Successfully!")