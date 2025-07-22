import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import re
import winreg
import ipaddress
import socket



#netsh advfirewall show allprofiles
def checkfirewall_status():
    try:
        output = subprocess.check_output("netsh advfirewall show allprofiles", shell=True, text=True)
        profiles = ['Domain', 'Private', 'Public']
        library = {}
        disabled_profiles = []

        for profile in profiles:
            # Find the section for the profile
            section_pattern = rf"{profile} Profile Settings:[\s\S]*?(?=(Domain|Private|Public) Profile Settings:|\Z)"
            section_match = re.search(section_pattern, output, re.IGNORECASE)
            if section_match:
                section = section_match.group(0)
                # Find the State line in the section
                state_match = re.search(r"State\s+([A-Z]+)", section)
                if state_match:
                    state = state_match.group(1).upper()
                    if state == "ON":
                        library[profile] = "ENABLED ||" 
                    else:
                        library[profile] = "DISABLED||"
                        disabled_profiles.append(profile)
                else:
                    library[profile] = "UNKNOWN"
            else:
                library[profile] = "UNKNOWN"                
        result =  "\n".join([f"{profile} Firewall: {status}" for profile, status in library.items()])
        if disabled_profiles:
            print("\n Warning, following profiles are DISABLED.\n")
        for profile in disabled_profiles:
            print(f"- {profile} -")
            user_input = input("would you like to enable all?  y/n")
            if user_input == "y":
                try:
                    subprocess.run([
                        "powershell",
                        "-Command",
                        "Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True"
                        ], check = True)
                    
                    result += "\n\n Firewall profiles enabled successfully."
                except subprocess.CalledProcessError:
                    result += "\n\n Cannot enable firewall profiles. Enable Manually."
                return result
        return result
    except Exception as e:
        return f"Error checking firewall status: {e}"
    
    
def check_windows_defender():
    try:
        cmd = [
            "powershell",
            "-Command",
            "Get-Service -Name WinDefend | Select-Object -ExpandProperty Status"
        ]
        #cmd = 'powershell -Command"Get-Service -Name WinDefend | Select-Object -ExpandProperty Status"'
        output = subprocess.check_output(cmd, shell=True, text=True).strip()

        if output:
            return f"windows defender:{output.upper()} ?"
        else:
            return "windows defender has no status"
    except subprocess.CalledProcessError:
        return "Windows defender could not be found"
    except Exception as e:
        return f"Error checking Windows Defender Status: {e}"

def regedit_check():
    entries = []


    def read_registry_entries(root,path,scope_label):
        try:
            with winreg.OpenKey(root,path) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        entries.append(f"  ||--[{scope_label}] {name} -> {value}\n")
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            entries.append(f"[{scope_label} registry path not found")
        except Exception as e:
            entries.append(f"[{scope_label} {e}")
    
    read_registry_entries(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "CurrentUser"
    )
    read_registry_entries(
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "LocalMachine"
    )

    return "\n".join(entries) if entries else "No registry entries found"
def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return f"Local IP Address: {local_ip}"
    except socket.error as e:
        return f"Error getting local IP address: {e}"
    
def ping_ip(ip):
    try:
        #pings once
        command = subprocess.check_output(["ping", "-n", "1","w","500",str(ip)])
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)     
        return str(ip) if result.returncode == 0 else None           
    except Exception:
        return None
     
def scan_network(subnet="auto"):
    # local_ip = get_local_ip()
    # if not local_ip:
    #     return "Could not determine local IP address."
    try:
        if subnet == "auto":
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            base_net = ipaddress.ip_network(local_ip + "/24", strict=False)
        else:
            base_net = ipaddress.ip_network(subnet, strict=False)
    
        print(f"Scanning network: {base_net}")
        live_hosts = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(ping_ip, base_net.hosts())
            for result in results:
                if result:
                    live_hosts.append(result)

        return "active devices on the network:\n" + "\n".join(live_hosts) if live_hosts else "No active devices found on the network."
    except Exception as e:
        return f"Error scanning network: {e}"
    

def scan_arp_table():
    try:
        output = subprocess.check_output("arp -a", shell=True, text=True)
        lines = output.splitlines()
        devices = []
    
        for line in lines:
            if "-" in line and "dynamic" in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    ip_address = parts[0]
                    mac_address = parts[1]
                    devices.append(f"IP: {ip_address}, MAC: {mac_address}")
        return "devices found via the arp table \n".join(devices) if devices else "No devices found in ARP table."
    except Exception as e:
        return f"Error scanning ARP table: {e}"
def listofusers():
    try:
        cmd1= [
            "powershell",
            "-Command",
            "Get-LocalUser | Select-Object -Property Name, Enabled, LastLogon, description | Format-Table -AutoSize"
            ]
        output = subprocess.check_output(cmd1, shell=True, text=True).strip()
        if output:
            users = output.splitlines()
            return "Users on the system:\n" + "\n".join(users)
        else:
            return "no users found"
    except subprocess.CalledProcessError:
        return "failed to access user list"
    except Exception as e:
        return f"Error checking users: {e}"
    
def corrupt_check():
    user_input = input("Wold you like to run a System File Check? (y/n)").strip().lower()
    if user_input not in ["y", "yes"]:
        return "System File Check not initiated."
    print("Running System File Check... this may take a while.")

    try:
        with subprocess.Popen([
            "cmd.exe",
            "/c",
            "sfc",
            "/scannow"
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        bufsize=1, 
        universal_newlines=True
    ) as process:
            show_chunks = set()

            for line in process.stdout:
                line = line.strip()

                match = re.search(r"Verification\s+(\d+)%\s+complete", line)

                if match:
                    percent = int(match.group(1))

                    for threshold in [0, 25, 50, 75, 100]:
                        if percent >= threshold and threshold not in show_chunks:
                            print(f"{threshold}% completed.")
                            show_chunks.add(threshold)
                elif "Windows Resource Protection" in line:
                    print(f"\n Result: {line}")

        return "\n System file check completed."
    except Exception as e:
        return f"Error running System File Check: {e}"
    
if __name__ == "__main__":
    print("\n           Welcome to the security tool          \n")
    print("--firewall status:  ")
    print("==========================")
    print(checkfirewall_status())
    print("==========================")
    #first section above
    print("=================================================================================================================================")
    print("\n ~~~ hey, is your: ~~~\n")
    print(check_windows_defender())
    print("   ...Well you better go catch it!\n")
    print("\n")
    print("=================================================================================================================================")
    print("when power is suplied to the computer, it will open:")
    print("🥁🥁🥁startup applications:🧨✨✨")
    print("\n" + regedit_check() + "\n")
    print("=================================================================================================================================")
    print("\n")
    print("starting network scan, do not turn of your computer, or the computer will not be able to scan your information")
    print("\n")
    print("its all good dude, kidding. these are the devices on your network:")
    print("\n" +  scan_arp_table()  + "\n")
    #print("ping version: \n" + scan_network() + "\n")
    print("=================================================================================================================================")
    print("\n")
    print("your local ip address is: \n" + get_local_ip() + "\n")
    print("=================================================================================================================================")
    print("\n")
    print("the users on your system are: \n" + listofusers() + "\n")
    print("=================================================================================================================================")
    print("\n")
    print(corrupt_check())
    print("\n")
    print("=================================================================================================================================")
    print("\n")
    print("😎 thank you for using the security tool, have a nice day! 😎"
          "\n")