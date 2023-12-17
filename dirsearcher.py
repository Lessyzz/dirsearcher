import time, requests, argparse, sys    
from requests.sessions import Session
from threading import Thread, local
from queue import Queue

class DirectorySearcher():
    def __init__(self):
        self.found_directories = []
        self.queue = Queue()
        self.thread_local = local()

        self.total = 0
        self.getArgs()
        self.openWordlist()
        self.printArgs()
        self.run()

    def getArgs(self):
        parser = argparse.ArgumentParser(description = 'Directory Searcher')
        parser.add_argument('-u', type = str, help = 'Target URL')
        parser.add_argument('-t', type = int, default = 150, help = 'Threads (150 default)')
        parser.add_argument('-w', type = str, help = 'Wordlist')

        args = parser.parse_args()

        self.url = args.u
        self.threads = args.t
        self.wordlistName = args.w

    def openWordlist(self):
        try:
            with open(self.wordlistName) as file:
                read = file.read()
                self.wordlist = read.split("\n")

                if self.url[-1] != "/":
                    self.url = self.url + "/"

                for dir in self.wordlist:
                    self.queue.put(f"{self.url}{dir}")
        except TypeError:
            sys.exit("Usage: dirsearcher.py -u <url> -t <threads> -w <wordlist>")

    def printArgs(self):
        print('\nUrl:', self.url)
        print('Threads:', self.threads)
        print('Wordlist:', self.wordlistName + "\n")       

    def get_session(self) -> Session:
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session

    def scan_url(self):
        thread_num = self.threads
        for i in range(thread_num):
            t_worker = Thread(target = self.scan_function)
            t_worker.start()
        self.queue.join()
        
    def scan_function(self):
        session = self.get_session()
        while True:
            url = self.queue.get()
            print(f"Searcing Directories: {self.total}/{len(self.wordlist)}", end = "\r")
            self.total += 1
            with session.get(url) as response:
                #print(f"Scanning {url}")
                if response.status_code == 200:
                    self.found_directories.append(url)
            self.queue.task_done()          

    def run(self):
        start = time.time()
        self.scan_url()
        end = time.time()

        print("=" * (len(self.url) + 15))
        for i in self.found_directories:
            print(i)
        print("=" * (len(self.url) + 15))

        print(f"\nSearched {len(self.wordlist)} directory in {end - start} seconds - Found {len(self.found_directories)} directory!\nDirectory Searcher - by Lessy")

run = DirectorySearcher()
