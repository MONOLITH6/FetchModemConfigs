import requests
from bs4 import BeautifulSoup
import subprocess
import os

# Modem IP and credentials
modem_ip = "10.1.10.1"
username = "cusadmin"
password = "highspeed"

# Cookie file path
cookie_file = "/home/kali/Desktop/Comcast/cookies.txt"

# Gowitness configuration
urls_to_scan = [
    f"http://{modem_ip}/at_a_glance.jst",
    f"http://{modem_ip}/initial_setup.jst",
    f"http://{modem_ip}/local_ip_configuration.jst",
    f"http://{modem_ip}/wireless_network_configuration_edit.jst?id=1",
    f"http://{modem_ip}/wireless_network_configuration_edit.jst?id=2",
    f"http://{modem_ip}/firewall_settings_ipv4.jst",
    f"http://{modem_ip}/firewall_settings_ipv6.jst",
    f"http://{modem_ip}/hardware.jst",
    f"http://{modem_ip}/connected_devices_computers.jst",
    f"http://{modem_ip}/port_forwarding.jst",
    f"http://{modem_ip}/port_triggering.jst",
    f"http://{modem_ip}/port_management.jst",
    f"http://{modem_ip}/remote_management.jst",
    f"http://{modem_ip}/dmz.jst",
    f"http://{modem_ip}/nat.jst",
    f"http://{modem_ip}/staticrouting.jst",
    f"http://{modem_ip}/device_discovery.jst"
]

# Adjust this path to your local Gowitness executable if needed
gowitness_path = "/usr/bin/gowitness"

# Function to save cookies to a file
def save_cookies(response_cookies):
    try:
        with open(cookie_file, "w") as f:
            for cookie in response_cookies:
                f.write(f"{cookie.domain}\t{cookie.path}\t{cookie.secure}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
        print("Cookies saved successfully.")
    except Exception as e:
        print(f"Error saving cookies: {e}")

# Function to load cookies from file
def load_cookies():
    cookies = {}
    try:
        with open(cookie_file, "r") as f:
            for line in f:
                if not line.startswith("#") and len(line.strip()) > 0:
                    parts = line.strip().split("\t")
                    if len(parts) >= 6:
                        cookies[parts[-2]] = parts[-1]
        print("Cookies loaded successfully.")
    except FileNotFoundError:
        print("Cookie file not found.")
    return cookies

# Attempt login to the modem
def login():
    print("Attempting to log in to the modem...")
    login_url = f"http://{modem_ip}/check.jst"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": f"http://{modem_ip}",
        "Referer": f"http://{modem_ip}/"
    }
    data = {
        "username": username,
        "password": password
    }

    try:
        session = requests.Session()
        response = session.post(login_url, headers=headers, data=data)

        if "Incorrect password" in response.text:
            print("Invalid credentials. Please check the username and password.")
            return None

        if "DUKSID" in response.cookies:
            print("Login successful.")
            save_cookies(response.cookies)
            return session
        else:
            print("Login failed. Unknown error.")
            return None
    except requests.RequestException as e:
        print(f"An error occurred during login: {e}")
        return None

# Fetch wireless settings
def fetch_wireless_settings(session, url, frequency):
    print(f"Fetching {frequency} GHz wireless settings...")

    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {frequency} GHz wireless settings. HTTP Status: {response.status_code}")
            return

        # Parse the response using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract SSID and Password
        ssid_tag = soup.find("input", {"id": "network_name"})
        password_tag = soup.find("input", {"id": "network_password"})

        ssid = ssid_tag["value"] if ssid_tag else "SSID not found"
        password = password_tag["value"] if password_tag else "Password not set or not found"

        print(f"SSID: {ssid}")
        print(f"Password: {password}")
    except requests.RequestException as e:
        print(f"An error occurred while fetching {frequency} GHz wireless settings: {e}")
    except Exception as e:
        print(f"Error parsing wireless settings: {e}")

# Run Gowitness on specified URLs
def run_gowitness(urls, cookie):
    print("Running Gowitness...")
    try:
        # Create a local file with URLs
        urls_file = "comcast-list.txt"
        with open(urls_file, "w") as f:
            for url in urls:
                f.write(f"{url}\n")

        # Construct the Gowitness command (no --destination)
        command = [
            gowitness_path,
            "scan",
            "file",
            "-f", urls_file,
            "--chrome-header", f"Cookie: DUKSID={cookie};",
            "--save-content"
        ]

        subprocess.run(command, check=True)
        print("Gowitness scan completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Gowitness: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Main
if __name__ == "__main__":
    cookies = load_cookies()
    if not cookies:
        session = login()
    else:
        session = requests.Session()
        session.cookies.update(cookies)

    if session:
        url_24g = f"http://{modem_ip}/wireless_network_configuration_edit.jst?id=1"
        url_5g = f"http://{modem_ip}/wireless_network_configuration_edit.jst?id=2"

        fetch_wireless_settings(session, url_24g, "2.4")
        fetch_wireless_settings(session, url_5g, "5")

        # Get DUKSID cookie
        duksid_cookie = session.cookies.get("DUKSID", domain=modem_ip)
        if duksid_cookie:
            run_gowitness(urls_to_scan, duksid_cookie)
        else:
            print("DUKSID cookie not found. Unable to run Gowitness.")
    else:
        print("Not logged in. Please log in and ensure the session is active.")
