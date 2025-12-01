"""
Gunicorn configuration for PM Tools Suite
Handles long-running AI document analysis requests
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', '2'))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings - CRITICAL for long-running AI analysis
# HOTDOG analysis can take 5-10 minutes for large documents
timeout = 900  # 15 minutes (in seconds)
graceful_timeout = 900  # 15 minutes
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
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

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting PM Tools Suite")
    server.log.info(f"Workers: {workers}, Timeout: {timeout}s")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"💀 Worker {worker.pid} interrupted")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.warning(f"⚠️ Worker {worker.pid} aborted (likely timeout)")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"👶 Worker {worker.pid} spawned")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("🔄 Forking new master process")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ Server is ready")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"👋 Worker {worker.pid} exited")

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info(f"📊 Workers changed: {old_value} → {new_value}")
