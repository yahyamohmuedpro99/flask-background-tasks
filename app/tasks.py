import time
from rq import Queue
from redis import Redis

# Initialize RQ queue
redis_instance = Redis()
queue_tasks = Queue(connection=redis_instance)

def background_task(n):
    delay = 15

    print("Task started and running now...")
    print(f"Simulating {delay} seconds of processing...")

    time.sleep(delay)

    print("Task finished")
    return len(n)
