class Worker:
    
    def __init__(self, worker_id, worker_pos, worker_status, on_from = 0):
        self.id = worker_id
        self.pos = worker_pos
        self.status = worker_status
        self.on_from = on_from
        self.travel = 0
        self.job_done = 0
        self.last_job_done_at = 0
        self.idle = 0
        self.wait = 0
        self.initial_pos = worker_pos
        self.initial_status = worker_status
        self.initial_on_from = on_from

    def reset(self):

        self.pos = self.initial_pos
        self.status = self.initial_status
        self.on_from = self.initial_on_from

        self.idle = 0
        self.wait = 0
        self.travel = 0
        self.job_done = 0
        
        


class WorkerManager:
    
    def __init__(self):
        self.workers = {}
    
    def set_worker(self, worker):
        self.workers[worker.id] = worker
        
    def get_next_on(self, threshold=50):

        minOn = 1000000
        who = None
        
        for w in self.workers:
            
            if self.workers[w].on_from < minOn:
                minOn = self.workers[w].on_from

        ret = []
        for w in self.workers:

            if minOn <= self.workers[w].on_from <= minOn + threshold:
                ret.append((w, self.workers[w].on_from))

        return ret

    def reset_workers(self):

        for w in self.workers:        
            self.workers[w].reset()
    

def gen_test_workerManager():
    wm = WorkerManager()

    wm.set_worker(Worker("WK_1", "DOOR_(1,0)", 1))
    wm.set_worker(Worker("WK_2", "DOOR_(7,0)", 1))
    wm.set_worker(Worker("WK_3", "DOOR_(13,0)", 1))
    wm.set_worker(Worker("WK_4", "DOOR_(19,0)", 1))
    wm.set_worker(Worker("WK_5", "DOOR_(25,0)", 1))

    return wm


if __name__ == "__main__":
    wm = WorkerManager()

    wm.set_worker(Worker("WK_1","DOOR_(1,0)",1))
    wm.set_worker(Worker("WK_2","DOOR_(7,0)",1))
    wm.set_worker(Worker("WK_3","DOOR_(13,0)",1))
    wm.set_worker(Worker("WK_4","DOOR_(19,0)",1))
    wm.set_worker(Worker("WK_5","DOOR_(25,0)",1))

    wm.workers['WK_1'].pos