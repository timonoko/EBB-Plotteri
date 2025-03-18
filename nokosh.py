import os

def sh(x):
    return os.popen(x).read().split("\n")

import sys
from pprint import pprint

# Define a custom display hook that uses pprint
def my_display_hook(value):
    if value is not None:  # REPL doesn't print None by default, so we skip it
        pprint(value)

print('Replace the default display hook with our custom one')
sys.displayhook = my_display_hook

    
