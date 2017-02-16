# import queue as queue
# import threading
# import requests
#
#
# # called by each thread
# def get_url(list, url):
#     response = requests.get(url)
#     list.append(response)
#
#
# urls = ["http://google.com", "http://yahoo.com"]
#
# # q = queue.Queue()
#
# list = []
#
# for u in urls:
#     t = threading.Thread(target=get_url, args=(list, u))
#     t.daemon = True
#     t.start()
#
# print(list)

# import grequests
#
# class Test:
#     def __init__(self):
#         self.urls = [
#             'http://www.example.com',
#             'http://www.google.com',
#             'http://www.yahoo.com',
#             'http://www.stackoverflow.com/',
#             'http://www.reddit.com/'
#             'http://www.manutd.com/'
#         ]
#
#     def exception(self, request, exception):
#         print("Problem: {}: {}".format(request.url, exception))
#
#     def async(self):
#         results = grequests.map((grequests.get(u) for u in self.urls), exception_handler=self.exception, size=5)
#         print(results)
#
# test = Test()
# test.async()

import queue as queue
from threading import Thread
from social_network_helper import get_historical_trends

keywords = ['Manchester United', 'Martial', 'Gal Gadot']

list = {}


def do_stuff(i, q):
    while True:
        print(i)
        term = q.get()
        results = get_historical_trends(term)
        list[term] = results
        q.task_done()


q = queue.Queue(maxsize=0)
num_threads = len(keywords)

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(i, q))
    worker.setDaemon(True)
    worker.start()

for keyword in keywords:
    q.put(keyword)

q.join()

print(list)

# for item in list:
#     print(item)
