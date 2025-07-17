import os, sys, subprocess, re, uuid, ctypes

class BypassVM:

    def registry_check(self):  
        # Check for VMware registry keys
        reg1 = subprocess.run("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        reg2 = subprocess.run("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if reg1.returncode == 0 or reg2.returncode == 0:
            sys.exit(0)

    def processes_and_files_check(self):
        vmware_dll = os.path.join(os.environ["SystemRoot"], "System32\\vmGuestLib.dll")
        virtualbox_dll = os.path.join(os.environ["SystemRoot"], "vboxmrxnp.dll")    
    
        try:
            process_output = subprocess.check_output('TASKLIST /FI "STATUS eq RUNNING"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW, text=True, errors='ignore')
        except Exception:
            process_output = ""
            
        if "VMwareService.exe" in process_output or "VMwareTray.exe" in process_output:
            sys.exit(0)
                           
        if os.path.exists(vmware_dll):
            sys.exit(0)
            
        if os.path.exists(virtualbox_dll):
            sys.exit(0)
        
        try:
            # Attempt to load Sandboxie DLL
            _ = ctypes.cdll.LoadLibrary("SbieDll.dll")
            sys.exit(0)
        except OSError:
            # SbieDll.dll not found or cannot be loaded, indicating no Sandboxie
            pass              

    def mac_check(self):
        mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        vmware_mac_list = ["00:05:69", "00:0c:29", "00:1c:14", "00:50:56"]
        if mac_address[:8] in vmware_mac_list:
            sys.exit(0)
                   
        
if __name__ == '__main__':
    test = BypassVM()
    test.registry_check()
    test.processes_and_files_check()
    test.mac_check()
