import os
import requests
import random
import threading
import sys
import time
from colorama import init, Fore

ENDPOINTS = ["mjpg/video.mjpg"]  # Array of endpoints to test
USER_AGENT_FILE = 'user_agents.txt'
IP_FILE = 'IPs.txt'
NUM_THREADS = 4
MAX_RUNTIME = 5 * 60 * 60  # 5 hours in seconds

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
    start_time = time.time()
    while time.time() - start_time < MAX_RUNTIME:
        ip_address = '.'.join(str(random.randint(0, 255)) for _ in range(4))
        selected_user_agent = random.choice(user_agents)
        headers = {'User-Agent': selected_user_agent}
        timeout = 2  # Timeout set to 2 seconds
        
        if not check_ip(ip_address):
            print(f"{Fore.RED}IP Address {ip_address} at port 80 did not respond.{Fore.RESET}")
            continue
        
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
    print("Thread finished execution.")

def scan(user_agents):
    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=scan_one, args=(user_agents,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    try:
        with open(USER_AGENT_FILE, 'r') as file:
            user_agents = [line.strip() for line in file if line.strip()]

        # Create IPs.txt if it doesn't exist
        if not os.path.exists(IP_FILE):
            with open(IP_FILE, 'w'):
                pass

        # Start scanning
        scan(user_agents)

        # Sleep to ensure all threads finish before exiting
        time.sleep(1)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Keyboard interrupt received. Exiting...{Fore.RESET}")
        sys.exit(0)
