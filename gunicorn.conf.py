import os
import multiprocessing

bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gthread'
threads = 2
worker_tmp_dir = '/dev/shm'
timeout = 120
graceful_timeout = 30
keepalive = 5
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
proc_name = 'vedyura'
preload_app = True
max_requests = 1000
max_requests_jitter = 50

def on_starting(server):
    print("Vedyura production server starting...")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")
