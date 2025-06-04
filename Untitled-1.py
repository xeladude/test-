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




if __name__ == "__main__":
    print("welcome to the security tool")
    print("firewall status:")
    print(checkfirewall_status())




























































































