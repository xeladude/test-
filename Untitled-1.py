import os
import subprocess
import re
#netsh advfirewall show allprofiles
def checkfirewall_status():
    try:
        output = subprocess.check_output("netsh advfirewall show allprofiles", shell=True, text=True)
        profiles = ['Domain', 'Private', 'Public']
        library = {}
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
                    library[profile] = "ENABLED" if state == "ON" else "DISABLED"
                else:
                    library[profile] = "UNKNOWN"
            else:
                library[profile] = "UNKNOWN"
        return "\n".join([f"{profile} Firewall: {status}" for profile, status in library.items()])
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
            return f"windows defender is :{output.upper()}"
        else:
            return "windows defender has no status"
    except subprocess.CalledProcessError:
        return "Windows defender could not be found"
    except Exception as e:
        return f"Error checking Windows Defender Status: {e}"











if __name__ == "__main__":
    print("=== Welcome to the security tool ===\n")
    print("== firewall status: == \n ")
    print(checkfirewall_status())
    print("\n ~~~ windows defender status is: ~~~\n")
    print(check_windows_defender())
    print("\n")























































































