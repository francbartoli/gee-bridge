bind = '0.0.0.0:9000'
# bind = 'unix:/tmp/supervisor.sock'
workers = 3
timeout = 120
capture_output = True
loglevel = "debug"
errorlog = '/tmp/gunicorn_error.log'
daemon = True
