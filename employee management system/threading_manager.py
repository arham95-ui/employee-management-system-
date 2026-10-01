import threading
import queue
import time
from datetime import datetime

class ThreadManager:
    def __init__(self):
        self.workers = []
        self.tasks = queue.Queue()
        self.running = True
        self.lock = threading.Lock()
        self.task_results = {}
        
    def start_workers(self, num_workers=3):
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"Worker-{i+1}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def _worker_loop(self):
        while self.running:
            try:
                task = self.tasks.get(timeout=1)
                if task is None:
                    continue
                task_id, func, args, kwargs = task
                try:
                    result = func(*args, **kwargs)
                    with self.lock:
                        self.task_results[task_id] = result
                except Exception as e:
                    with self.lock:
                        self.task_results[task_id] = f"ERROR: {str(e)}"
            except queue.Empty:
                continue
    
    def submit_task(self, func, *args, **kwargs):
        task_id = f"{datetime.now().timestamp()}-{threading.get_ident()}"
        self.tasks.put((task_id, func, args, kwargs))
        return task_id
    
    def get_result(self, task_id, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.lock:
                if task_id in self.task_results:
                    result = self.task_results.pop(task_id)
                    if isinstance(result, str) and result.startswith("ERROR:"):
                        raise Exception(result[7:])
                    return result
            time.sleep(0.1)
        raise TimeoutError(f"Task {task_id} timed out")
    
    def shutdown(self):
        self.running = False
        for worker in self.workers:
            worker.join(timeout=2)

thread_manager = ThreadManager()