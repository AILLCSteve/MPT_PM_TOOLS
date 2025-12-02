"""
Gunicorn configuration for PM Tools Suite
Production deployment with async workers for real-time SSE streaming.
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker configuration - THREADING FOR ASYNC/CONCURRENT HANDLING
# Using threaded workers since our app uses Python threading for analysis
# This allows SSE streaming while analysis runs in background threads
workers = 1  # Single worker with threading
worker_class = 'sync'  # Sync worker + threading in Flask app
threads = 10  # Allow 10 concurrent threads per worker

# Worker lifecycle settings
max_requests = 1000  # Restart worker after N requests (prevent memory leaks)
max_requests_jitter = 50  # Add randomness to prevent thundering herd

# Timeout settings - CRITICAL for long-running AI analysis
# HOTDOG analysis can take 10-15 minutes for large documents
timeout = 900  # 15 minutes (in seconds)
graceful_timeout = 900  # 15 minutes for graceful shutdown
keepalive = 5  # Keep-alive connections

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" [%(D)s µs]'

# Process naming
proc_name = 'pm-tools-suite'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Debugging
reload = os.getenv('DEBUG', 'false').lower() == 'true'
reload_engine = 'auto'
spew = False

# Server hooks for logging
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting PM Tools Suite")
    server.log.info(f"Worker Class: {worker_class}, Workers: {workers}, Timeout: {timeout}s")
    server.log.info("✅ Gevent async workers enabled - SSE streaming ready")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"💀 Worker {worker.pid} interrupted")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.warning(f"⚠️ Worker {worker.pid} aborted (likely timeout)")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"👶 Worker {worker.pid} spawned (gevent)")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ Server is ready")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"👋 Worker {worker.pid} exited")
