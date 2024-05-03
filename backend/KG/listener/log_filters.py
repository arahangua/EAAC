import os,sys
from functools import wraps
import time


# functions for handling empty logs
def retry_on_error(max_retries=10, delay=2):
    """
    Decorator to retry a function that makes an getlog request again if the log is empty

    :param max_retries: Maximum number of retry attempts.
    :param delay: Delay between retries in seconds.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                response = func(*args, **kwargs)
                if len(response)==0:
                    print(f'request returned empty logs, it is expected if no matching logs were found.')
                    return None
                elif response.code == 200:
                    return response
                print(f"Attempt {attempt + 1} of {max_retries} as non 200 response code was returned. Retrying in {delay} seconds...")
                time.sleep(delay)
            print("Max retries reached. Request failed.")
            return None
        return wrapper
    return decorator

# check if its in checksum address
def make_filter(args):
    if(len(args['topics'])>0):
        return {'fromBlock': int(args['fromBlock']), 'toBlock': int(args['toBlock']), 'address': args['address'], 'topics': args['topics']} #topics is the list of keccak256 encoded function signatures
    else:
        return {'fromBlock': int(args['fromBlock']), 'toBlock': int(args['toBlock']), 'address': args['address']}

