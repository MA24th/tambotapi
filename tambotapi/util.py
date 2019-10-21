import threading

thread_local = threading.local()
# per_thread
def per_thread(key, construct_value, reset=False):
    if reset or not hasattr(thread_local, key):
        value = construct_value()
        setattr(thread_local, key, value)

    return getattr(thread_local, key)