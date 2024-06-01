import time
def background_task(n):
    delay = 15

    print("Task started and running now...")
    print(f"Simulating {delay} seconds of processing...")

    time.sleep(delay)

    print("Task finished")
    return len(n)
