#!/bin/bash

# Modem IP
modem_ip="10.1.10.1"

# Credentials
username="cusadmin"
password="highspeed"

# Attempt login
echo "Attempting to log in to the modem..."
login_response=$(curl -s -i -c cookies.txt -d "username=$username&password=$password" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Origin: http://$modem_ip" \
  -H "Referer: http://$modem_ip/" \
  -X POST "http://$modem_ip/check.jst")

# Check for invalid password message
if echo "$login_response" | grep -q "Incorrect password"; then
    echo "Invalid credentials. Please check the username and password."
    exit 1
fi

# Check for successful login (cookie presence indicates success)
if grep -q "DUKSID" cookies.txt; then
    echo "Login successful."
else
    echo "Login failed. Unknown error."
    exit 1
fi

# Fetch wireless settings
echo -e "\nFetching wireless settings..."
wireless_page=$(curl -s -b cookies.txt "http://$modem_ip/wireless_settings")

if [[ -n "$wireless_page" ]]; then
    # Parse SSID and encryption type (example parsing)
    ssid=$(echo "$wireless_page" | grep -oP '(?<=<ssid>).*?(?=</ssid>)')
    encryption=$(echo "$wireless_page" | grep -oP '(?<=<encryption>).*?(?=</encryption>)')

    echo "SSID: $ssid"
    echo "Encryption: $encryption"
else
    echo "Unable to fetch wireless settings. Ensure the URL is correct."
fi
