from threading import Thread
from queue import Queue
import requests
import re


class RequestQueue(Queue):
    def __init__(self, num_workers=1):
        Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()
        self.task_counter = 0
        self.results = []

    def send_request(self,
                     method='get',
                     url=None,
                     payload={},
                     num_repeats=3,
                     auth_user='',
                     auth_pass=''):
        task = locals()
        del task['self']
        self.put((task, self.task_counter))
        self.task_counter += 1

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            task = self.get()
            if task is None:
                break
            self.do_work(task[0], task[1])
            self.task_done()

    def do_work(self, task, task_number):
        # print ("I'm working on this {0}".format(task))
        # print (locals())
        # send the request and make sure the status is 200
        status = False
        repeat = 0
        r = None
        error = ''
        while not status and repeat < task['num_repeats']:
            try:
                r = requests.request(task['method'],
                                     task['url'],
                                     auth=(task['auth_user'], task['auth_pass']))
                status = re.search(r"2[0-9][0-9]$", str(r.status_code)) is not None
                repeat += 1
            except requests.exceptions.Timeout as e:
                error = e
                repeat += 1
            except requests.exceptions.TooManyRedirects as e:
                error = e
                repeat += 1
            except requests.exceptions.RequestException as e:
                # catastrophic error. bail.
                error = e
                repeat += 1

        if r is not None:
            self.results.append((r, task_number))
        else:
            self.results.append((error, task_number))

    def get_results(self, sort=True):
        if sort:
            self.results = sorted(self.results, key=lambda x: x[1])

        return list(map(lambda x: x[0], self.results))


def tests():
    q = RequestQueue(num_workers=5)
    url = 'https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json'
    wrong_url = 'https://1openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json'
    for item in range(10):
        q.send_request(method='get',
                       url=wrong_url,
                       payload={}
                       )

    q.join()
    results = q.get_results()
    for result in results:
        print (result)
        pass

    # block until all tasks are done
    print ("All done!")


if __name__ == "__main__":
    tests()
