# import concurrent.futures
# import logging
# import threading
# import time

# def thread_function(name):
#     logging.info("Thread %s: starting", name)
#     time.sleep(2)
#     logging.info("Thread %s: finishing", name)

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")

#     # threads = list()
#     # for index in range(3):
#     #     logging.info("Main    : create and start thread %d.", index)
#     #     x = threading.Thread(target=thread_function, args=(index,))
#     #     threads.append(x)
#     #     x.start()

#     # for index, thread in enumerate(threads):
#     #     logging.info("Main    : before joining thread %d.", index)
#     #     thread.join()
#     #     logging.info("Main    : thread %d done", index)
#     test = ["1","2","3"]
#     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#         executor.submit(thread_function,test)

def myFunc():
    for i in range(5):
        print(i)
        if i == 2:
            return

myFunc()

