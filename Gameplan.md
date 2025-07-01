1. Check windows firewall status. yes - DEFINITLY FIXED

2. Is windows defender running? yes

3. Check for startup app entires. Done!
    # Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    # #Computer\HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run

4. list all installed by size going largest to lowest

5. if firewall is down, ask prompt to turn on firewall.
-- Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True


Next Class, we will get the startup apps from the regedit directory. We need both paths.