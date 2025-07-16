import os, sys, subprocess, re, uuid, ctypes

class BypassVM:

    def registry_check(self):  
        reg1 = os.system("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2> nul")
        reg2 = os.system("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2> nul")       
        
        if reg1 != 1 and reg2 != 1:    
            # print("VMware Registry Detected") # Removed for stealth
            sys.exit()

    def processes_and_files_check(self):
        vmware_dll = os.path.join(os.environ["SystemRoot"], "System32\\vmGuestLib.dll")
        virtualbox_dll = os.path.join(os.environ["SystemRoot"], "vboxmrxnp.dll")    
    
        try:
            process_output = subprocess.check_output('TASKLIST /FI "STATUS eq RUNNING"',
                                                     shell=True,
                                                     creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8', errors='ignore')
        except Exception:
            process_output = ""
            
        if "VMwareService.exe" in process_output or "VMwareTray.exe" in process_output:
            # print("VMwareService.exe & VMwareTray.exe process are running") # Removed for stealth
            sys.exit()
                           
        if os.path.exists(vmware_dll): 
            # print("Vmware DLL Detected") # Removed for stealth
            sys.exit()
            
        if os.path.exists(virtualbox_dll):
            # print("VirtualBox DLL Detected") # Removed for stealth
            sys.exit()
        
        try:
            sandboxie = ctypes.cdll.LoadLibrary("SbieDll.dll")
            # print("Sandboxie DLL Detected") # Removed for stealth
            sys.exit()
        except OSError:
            pass              

    def mac_check(self):
        mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        vmware_mac_list = ["00:05:69", "00:0c:29", "00:1c:14", "00:50:56"]
        if mac_address[:8] in vmware_mac_list:
            # print("VMware MAC Address Detected") # Removed for stealth
            sys.exit()
                   
        
if __name__ == '__main__':
    test = BypassVM()
    test.registry_check()
    test.processes_and_files_check()
    test.mac_check()