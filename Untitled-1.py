import os
import subprocess
import re
import winreg
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






















































































