# ISP Scrapper Tool

## Overview
The ISP Scrapper Tool is a Python-based utility designed to fetch and display public/private IP addresses, retrieve wireless network settings (SSID and password) from a modem, and capture screenshots of modem configuration pages using **Gowitness**. The tool can log into a modem, save cookies for session reuse, and provide detailed network information.

## Features
- Fetches public and private IP addresses.
- Retrieves SSID and password for 2.4GHz and 5GHz wireless networks.
- Uses **Gowitness** to capture screenshots of modem configuration pages.
- Supports dynamic gateway IP input.
- Reuses saved cookies for efficient session handling.
- Deletes temporary files after processing.

## Prerequisites
1. **Python**: Ensure Python 3.6 or later is installed.
2. **Dependencies**: Install the required Python libraries using:
   ```bash
   pip install requests beautifulsoup4
   ```
3. **Gowitness**: Install Gowitness in `/usr/bin/gowitness`. Follow the [Gowitness installation guide](https://github.com/sensepost/gowitness).

## How It Works
1. **Gateway IP**: The tool prompts for the modem's gateway IP. The default is `10.1.10.1`, but a custom IP can be provided.
2. **Login**: Logs into the modem using credentials (`cusadmin`/`highspeed`) and saves session cookies.
3. **Wireless Settings**: Fetches SSID and password for both 2.4GHz and 5GHz networks.
4. **Public/Private IPs**: Displays the public and private IP addresses.
5. **Screenshot Capture**: Uses Gowitness to take screenshots of the modem's configuration pages and saves them to a specified folder.

## Usage
Run the script using:
```bash
python3 isp_scrapper.py
```

### Step-by-Step Instructions
1. **Gateway IP**: The script will prompt:
   ```bash
   Is the gateway IP the standard 10.1.10.1? (yes/no):
   ```
   - Type `yes` to use the default.
   - Type `no` and input the custom gateway IP.

2. **Output Directory**: For screenshots, the tool will prompt:
   ```bash
   Please enter the screenshot output folder path:
   ```
   Provide a valid directory path where Gowitness screenshots will be saved.

3. **Execution**: The tool performs the following:
   - Logs into the modem.
   - Fetches and displays public/private IPs.
   - Retrieves SSID and passwords for 2.4GHz and 5GHz networks.
   - Captures screenshots of configuration pages using Gowitness.

### Example
```bash
python3 isp_scrapper.py
```
- Default gateway IP: `10.1.10.1`.
- Screenshots saved in the specified folder.

## Files and Directories
- **`isp_scrapper.py`**: Main script file.
- **`cookies.txt`**: Stores session cookies for reuse. Deleted automatically at runtime.
- **`comcast-list.txt`**: Temporary file for URLs to scan. Deleted after execution.

## Functions
### `is_valid_ip(ip)`
Validates an IPv4 address.

### `get_gateway_ip()`
Prompts the user for the modem gateway IP.

### `show_public_private_ips()`
Fetches and displays public/private IP addresses.

### `fetch_wireless_settings(session, url, frequency)`
Retrieves the SSID and password for the given frequency (2.4GHz/5GHz).

### `run_gowitness(urls, cookie)`
Captures screenshots of specified URLs using Gowitness.

### `save_cookies(response_cookies)`
Saves session cookies to `cookies.txt`.

### `load_cookies()`
Loads cookies from `cookies.txt` if available.

### `login()`
Logs into the modem and saves the session cookies.

### `main()`
Main function orchestrating the workflow.

## Example Output
### Public/Private IPs:
```plaintext
Public IP: 203.0.113.45
Private IP: 192.168.1.100
```

### Wireless Settings:
```plaintext
Fetching 2.4GHz wireless settings...
SSID (2.4GHz): MyHomeWiFi
Password (2.4GHz): P@ssw0rd123

Fetching 5GHz wireless settings...
SSID (5GHz): MyHomeWiFi_5G
Password (5GHz): StrongP@ssw0rd
```

### Gowitness Output:
```plaintext
Screenshots saved to: /home/user/screenshots
```

## Troubleshooting
- **Invalid Gateway IP**: Ensure the modem is reachable at the provided IP.
- **Gowitness Errors**: Verify Gowitness is installed and accessible at `/usr/bin/gowitness`.
- **Dependencies**: Install missing dependencies using `pip install -r requirements.txt`.

## Contributing
Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

This documentation template is ready for use on GitHub. Let me know if you'd like to tweak any section!