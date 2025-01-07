import colorama
import threading
import urllib3
import urllib.parse
import requests

from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
from tqdm import tqdm

colorama.init(autoreset=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Checker(object):
    def __init__(self, urls):
        self.urls = urls
        self.lock = threading.Lock()
        self.results_file = open("Results.txt", 'a')
        self.pbar = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; HarmonyOS; AGS3K-W09; HMSCore 6.10.4.302) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 HuaweiBrowser/13.0.5.303 Safari/537.36",
            "referer": "https://www.google.com",
            "origin": "https://www.google.com"

        }
    def normalize_urls(self):
        normalized_urls = []
        # can be optimized for in-place modification
        for url in self.urls:
            url = url.strip().rstrip()
            if ':443' in url:
                url = f"https://{url}"
            elif ':80' in url:
                url = f"http://{url}"
            else:
                normalized_urls.append(f"https://{url}")
                normalized_urls.append(f"http://{url}")
                
                # normalized_urls.append(f"https://{url}/roundcubemail")
                # normalized_urls.append(f"http://{url}/roundcubemail")
                continue
            
            # normalized_urls.append(url+'/roundcubemail')
            normalized_urls.append(url)
        self.urls = normalized_urls

    def check_url(self, url):
        try:
            url = f"{url}"
            req = requests.get(
                url=url,
                headers=self.headers,
                timeout=30,
                verify=False
            )
            # because different languages won't have the same "The installer is disabled!" message.
        except Exception as err:
            # failed to request, exit.
            # print(err)
            self.pbar.update()
            return
        
        # now get the redirect path
        # this is important because some sites may have it as /mail or /roundemail or /login
        try:
            url = req.url+'/installer'
            if ("$config['enable_installer'] = true" in req.text) or ("<h3>Checking PHP version</h3>" not in req.text):
                # it's disabled
                # print(f"{Fore.REd}disabled")
                self.pbar.update()
                return
            
            self.lock.acquire()
            self.results_file.write(f"{url}\n")
            self.results_file.flush()
            print(f"{Fore.GREEN}[ {url} ]")
            self.lock.release()
            self.pbar.update()
        except Exception as err:
            self.pbar.update()
            pass
    def main(self):
        self.normalize_urls()
        self.pbar = tqdm(total=len(self.urls), desc="Checking...")

        # self.check_url("http://216.239.133.150")
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map( self.check_url, self.urls )


if __name__ == "__main__":
    urls = list(set(open("urls.txt", 'r').readlines()))
    checkerObj = Checker( urls )
    checkerObj.main()
        
