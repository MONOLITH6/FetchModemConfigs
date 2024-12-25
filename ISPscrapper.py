import requests
from bs4 import BeautifulSoup
import subprocess
import os
import socket
from datetime import datetime
import re

def is_valid_ip(ip):
    """Validate an IPv4 address."""
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading zeros)
            (?:[1-9]\d{0,2})
          )
          \.
        ){3}
        (?:
          (?:[1-9]\d{0,2})
        )
        $
    """, re.VERBOSE)
    if pattern.match(ip):
        parts = ip.split(".")
        return all(0 <= int(part) <= 255 for part in parts)
    return False

def get_gateway_ip():
    """Prompt the user to confirm or enter a gateway IP."""
    default_ip = "10.1.10.1"
    while True:
        response = input(f"Is the gateway IP the standard {default_ip}? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return default_ip
        elif response in ['no', 'n']:
            custom_ip = input("Please enter the gateway IP address: ").strip()
            if is_valid_ip(custom_ip):
                return custom_ip
            else:
                print("Invalid IP address format. Please try again.")
        else:
            print("Please respond with 'yes' or 'no'.")

# Gateway IP determined by user input
modem_ip = get_gateway_ip()

# Modem credentials
username = "cusadmin"
password = "highspeed"

# Cookie file path
cookie_file = "cookies.txt"

# Gowitness path - adjust if needed
gowitness_path = "/usr/bin/gowitness"

# Array of URLs to scan
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

def save_cookies(response_cookies):
    """Save cookies to a file in Netscape format."""
    try:
        with open(cookie_file, "w") as f:
            for cookie in response_cookies:
                f.write(f"{cookie.domain}\t{cookie.path}\t{cookie.secure}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
        print("Cookies saved successfully.")
    except Exception as e:
        print(f"Error saving cookies: {e}")

def load_cookies():
    """Load cookies from file into a dictionary."""
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

def login():
    """Attempt to log in to the modem and save DUKSID cookie."""
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

def fetch_wireless_settings(session, url, frequency):
    """Fetch and print the SSID and password for the specified frequency band."""
    print(f"Fetching {frequency} GHz wireless settings...")

    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {frequency} GHz wireless settings. HTTP Status: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        ssid_tag = soup.find("input", {"id": "network_name"})
        password_tag = soup.find("input", {"id": "network_password"})

        ssid = ssid_tag["value"] if ssid_tag else "SSID not found"
        password = password_tag["value"] if password_tag else "Password not set or not found"

        print(f"SSID ({frequency} GHz): {ssid}")
        print(f"Password ({frequency} GHz): {password}")
    except requests.RequestException as e:
        print(f"An error occurred while fetching {frequency} GHz wireless settings: {e}")
    except Exception as e:
        print(f"Error parsing wireless settings: {e}")

def show_public_private_ips():
    """
    Fetch and display your public and private IP addresses.
    Public IP is retrieved via a simple HTTP call to a free service.
    Private IP is retrieved by resolving hostname with socket.
    """
    try:
        # Public IP
        public_ip = requests.get("https://api.ipify.org").text.strip()
    except Exception as e:
        public_ip = f"Unable to retrieve public IP ({e})"

    try:
        # Private IP
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)
    except Exception as e:
        private_ip = f"Unable to retrieve private IP ({e})"

    print(f"\nPublic IP:  {public_ip}")
    print(f"Private IP: {private_ip}\n")

def run_gowitness(urls, cookie):
    """Run Gowitness on the array of URLs using the provided DUKSID cookie."""
    print("Running Gowitness...")

    # Ask user for the screenshot output location
    screenshot_path = input("Please enter the screenshot output folder path: ").strip()

    # Validate screenshot_path
    if not screenshot_path:
        print("No screenshot path was provided. Exiting.")
        return

    # Create the directory if it doesn't exist
    try:
        os.makedirs(screenshot_path, exist_ok=True)
        print(f"Screenshots will be saved to: {screenshot_path}")
    except Exception as e:
        print(f"Failed to create directory '{screenshot_path}': {e}")
        return

    # Create a temporary file to store the URLs
    temp_file = "comcast-list.txt"
    try:
        with open(temp_file, "w") as f:
            for url in urls:
                f.write(url + "\n")

        # Construct the Gowitness command, including --screenshot-path
        command = [
            gowitness_path,
            "scan",
            "file",
            "-f", temp_file,
            "--chrome-header", f"Cookie: DUKSID={cookie};",
            "--save-content",
            "--screenshot-path", screenshot_path
        ]

        # Execute the Gowitness command
        subprocess.run(command, check=True)
        print(f"Gowitness scan completed successfully. Screenshots saved to '{screenshot_path}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Gowitness: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Remove the temporary file if you don't want to keep it
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"Temporary file '{temp_file}' removed.")
            except Exception as e:
                print(f"Failed to remove temporary file '{temp_file}': {e}")

def main():
    """Main function to orchestrate the workflow."""
    # Load cookies if available
    cookies = load_cookies()

    if not cookies:
        session = login()
    else:
        # If cookies exist, just reuse them
        session = requests.Session()
        session.cookies.update(cookies)
        print("Reusing existing session from cookies.")

    if session:
        # Display public/private IPs
        show_public_private_ips()

        # Fetch 2.4GHz wireless info
        url_24g = f"http://{modem_ip}/wireless_network_configuration_edit.jst?id=1"
        # Fetch 5GHz wireless info
        url_5g = f"http://{modem_ip}/wireless_network_configuration_edit.jst?id=2"

        fetch_wireless_settings(session, url_24g, "2.4")
        fetch_wireless_settings(session, url_5g, "5")

        # Retrieve DUKSID cookie for Gowitness
        duksid_cookie = session.cookies.get("DUKSID", domain=modem_ip)
        if duksid_cookie:
            # Run Gowitness with all URLs in urls_to_scan
            run_gowitness(urls_to_scan, duksid_cookie)
        else:
            print("DUKSID cookie not found. Unable to run Gowitness.")
    else:
        print("Not logged in. Please log in and ensure the session is active.")

if __name__ == "__main__":
    main()
