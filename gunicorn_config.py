"""
Gunicorn configuration for production deployment
Optimized for handling thousands of concurrent users
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
# Use gevent workers for async I/O and better concurrency
worker_class = 'gevent'

# Calculate workers: (2 x CPU cores) + 1
# But cap at 4 to avoid overwhelming external APIs
workers = min(4, (2 * multiprocessing.cpu_count()) + 1)

# Worker connections for gevent
# Higher value allows more concurrent connections per worker
worker_connections = 1000

# Timeout settings
# Increased timeout for image generation which can take longer
timeout = 120
keepalive = 5

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'dioramacast'

# Server hooks for graceful shutdown
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Gunicorn server")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"Worker {worker.pid} received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker is killed by timeout."""
    worker.log.info(f"Worker {worker.pid} was killed by timeout")

# Preload app for better performance
preload_app = True

# Max requests per worker before restart (prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Graceful timeout for workers
graceful_timeout = 30
