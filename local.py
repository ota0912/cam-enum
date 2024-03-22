import os
import requests
import random
import threading
import sys
from colorama import init, Fore

ENDPOINTS = ["mjpg/video.mjpg"]  # Array of endpoints to test
USER_AGENT_FILE = 'user_agents.txt'
IP_FILE = 'IPs.txt'
NUM_THREADS = 4

# Initialize colorama
init()

def check_ip(ip_address):
    try:
        response = requests.head(f"http://{ip_address}:80", timeout=2, verify=False)
        response.raise_for_status()  # Ensure no HTTP errors occurred
        return True
    except requests.RequestException:
        return False

def is_cam(headers):
    content_type = headers.get('Content-Type', '')
    return content_type == 'multipart/x-mixed-replace; boundary=myboundary'

def save_ip(ip_address, endpoint):
    with open(IP_FILE, 'a') as file:
        file.write(f"http://{ip_address}/{endpoint}\n")

def scan_one(user_agents):
    #ip_address = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    ip_address = "77.110.203.114"
    selected_user_agent = random.choice(user_agents)
    headers = {'User-Agent': selected_user_agent}
    timeout = 2  # Timeout set to 2 seconds
    
    if not check_ip(ip_address):
        print(f"{Fore.RED}IP Address {ip_address} at port 80 did not respond.{Fore.RESET}")
        return
    
    for endpoint in ENDPOINTS:
        url = f"http://{ip_address}/{endpoint}"
        try:
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True, verify=False)
            if response.status_code == 200:
                print(f"{Fore.GREEN}http://{ip_address}/{endpoint}{Fore.RESET}")
                print(f"{Fore.GREEN}Generated IP Address: {ip_address}, Endpoint: {endpoint}{Fore.RESET}")
                print(f"User Agent: {selected_user_agent}")
                print("Response Headers:")
                for header, value in response.headers.items():
                    print(f"{header}: {value}")
                if is_cam(response.headers):
                    print(f"{Fore.GREEN}Response suggests it's from a camera. Saving IP to {IP_FILE}{Fore.RESET}")
                    save_ip(ip_address, endpoint)
            else:
                print(f"{Fore.RED}Received response with status code {response.status_code}. Skipping processing.{Fore.RESET}")
        except requests.RequestException as e:
            print(f"{Fore.RED}Failed to retrieve headers from http://{ip_address}/{endpoint}: {e}{Fore.RESET}")

def scan(user_agents):
    while True:
        scan_one(user_agents)

if __name__ == "__main__":
    try:
        with open(USER_AGENT_FILE, 'r') as file:
            user_agents = [line.strip() for line in file if line.strip()]

        # Create IPs.txt if it doesn't exist
        if not os.path.exists(IP_FILE):
            with open(IP_FILE, 'w'):
                pass

        threads = []
        for _ in range(NUM_THREADS):
            thread = threading.Thread(target=scan, args=(user_agents,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print(f"{Fore.RED}Keyboard interrupt received. Exiting...{Fore.RESET}")
        sys.exit(0)
