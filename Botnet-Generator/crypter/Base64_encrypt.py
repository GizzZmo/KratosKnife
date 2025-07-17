import base64

class Encrypt:
    def __init__(self):
        self.text = ""
        self.enc_txt = ""

    def encrypt(self, filename):
        
        try:
            with open(filename, "r", encoding="utf8") as f:
                lines_list = f.readlines()
                self.text = "".join(lines_list).encode('utf-8') # Join and then encode to bytes
                  
                self.enc_txt =  base64.b64encode(self.text).decode('utf-8') # Encode to base64 bytes, then decode to string for literal

            with open(filename, "w") as f:
                # Embed the base64 encoded string literal for b64decode
                f.write(f"import base64; exec(base64.b64decode('{self.enc_txt}'))")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except Exception as e:
            raise Exception(f"An error occurred during Base64 encryption: {e}")
            
    
if __name__ == '__main__':   
    filename = input("[?] Enter Filename to encrypt: ")
    
    print(f"\n[*] Initaiting Base64 Encryption Process ...")    
    try:
        test = Encrypt()
        test.encrypt(filename)
        print(f"[+] Operation Completed Successfully!\n")
    except FileNotFoundError as e:
        print(f"[!] Error: {e}")
    except Exception as e:
        print(f"[!] Error: {e}")
