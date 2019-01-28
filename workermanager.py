class Worker:
    
    def __init__(self, worker_id, worker_pos, worker_status, on_from = 0):
        self.id = worker_id
        self.pos = worker_pos
        self.status = worker_status
        self.on_from = on_from
        self.travel = 0
        self.job_done = 0
        
        


class WorkerManager:
    
    def __init__(self):
        self.workers = {}
    
    def set_worker(self, worker):
        self.workers[worker.id] = worker
        
    def get_next_on(self):
        
        minOn = 1000000
        who = None
        
        for w in self.workers:
            
            if self.workers[w].on_from < minOn:
                minOn = self.workers[w].on_from
                who = [w]
            elif self.workers[w].on_from == minOn:
                who = who + [w]
        
        return minOn, who


if __name__ == "__main__":
    wm = WorkerManager()

    wm.set_worker(Worker("WK_1","DOOR_(1,0)",1))
    wm.set_worker(Worker("WK_2","DOOR_(7,0)",1))
    wm.set_worker(Worker("WK_3","DOOR_(13,0)",1))
    wm.set_worker(Worker("WK_4","DOOR_(19,0)",1))
    wm.set_worker(Worker("WK_5","DOOR_(25,0)",1))

    wm.workers['WK_1'].pos