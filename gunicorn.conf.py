import multiprocessing

bind = "0.0.0.0:8080"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "dht_torznab.api.main:app"
accesslog = "-"
