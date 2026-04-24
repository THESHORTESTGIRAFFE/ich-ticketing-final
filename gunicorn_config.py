import multiprocessing
import os

bind = "0.0.0.0:" + os.environ.get("PORT", "5000")
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120
keepalive = 5
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
