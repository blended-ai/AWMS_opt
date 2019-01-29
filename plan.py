from copy import deepcopy
import random
import methods
import pandas as pd

from itemmanager import ItemManager
from itemmanager import ItemAttribute
from workermanager import WorkerManager
from workermanager import Worker
from jobmanager import JobManager
from order import Order
from warehouse import Warehouse
import json


class Plan:
    
    def __init__(self, WH, workerManager, jobManager, itemManager):
        
        self.original_itemManager = itemManager
        self.original_jobManager = jobManager
        self.original_workerManager = workerManager
        self.wareHouse = WH
        
    def get_next_job(self, jobList):
        
        target = jobList[jobList['DONE'] == -1]

        if len(target) > 0:
            target_id = target.iloc[0]['JOB_ID']
            
            target = target[target['JOB_ID'] == target_id]
            dest = target.iloc[0]['DEST']
            start_from = max(target['START'])
            idxs = target.index

            print(target_id)
            print(target)
            
            return list(target['ITEM'].values), dest, start_from, idxs
        else :
            return [], 'a','b',[]
        
        
    def do_plan_assignment(self):
        
        itemM = deepcopy(self.original_itemManager)
        jobM = deepcopy(self.original_jobManager)
        workerM = deepcopy(self.original_workerManager)
        
        done = False
        
        
        jobList  = jobM.policyJobByOrder()
        print(jobList)
        jobList['DONE'] = -1
        jobList['DONE_BY'] = ''
        
        ret_coords = []
        ret_order_id = []
        ret_job_id = []
        ret_job_items = []
        ret_workers = []

        cur_time = 0

        while not done:
            
            nextEvent , workers = workerM.get_next_on()
            
            cur_time = nextEvent
            
            worker = random.choices(workers, k=1)[0]
            
            job, dest, start, idxs = self.get_next_job(jobList)

            if len(job) < 1:
                break
            
            origien_zone = self.wareHouse.zone_door_map[workerM.workers[worker].pos]
            dest_zone = self.wareHouse.zone_door_map[dest]
            
            p, m = methods.dive_in(self.wareHouse.WH_abstract_graph, self.wareHouse.zone_counter, origien_zone , dest_zone, job)
            print(jobList.loc[idxs[0]]['JOB_ID'])
            print(worker, job, p, m)
            
            result = methods.get_detail_and_consume(self.wareHouse, self.wareHouse.zone_counter, p, job, itemM)
            
            fp = methods.find_path(self.wareHouse.WH_graph,itemM,result)
            
            route, consumed_time = methods.path2Coords(self.wareHouse.WH_graph, fp, nextEvent)
            ret_coords.append(route)
            ret_job_id.append(jobList.loc[idxs[0]]['JOB_ID'])
            t_orders = list(jobList.loc[idxs]['ORDER_ID'].values)
            t_items = list(jobList.loc[idxs]['ITEM'].values)

            sub_ = []
            for to, ti in zip(t_orders, t_items):
                sub_.append((to,ti))


            #ret_job_items.append(job)
            ret_job_items.append(sub_)
            ret_workers.append(worker)
            
            so_time = max(consumed_time + cur_time ,start)
            
            workerM.workers[worker].on_from = so_time
            
            workerM.workers[worker].travel = consumed_time
            workerM.workers[worker].job_done += 1
            
            col_done = pd.Series([so_time]*len(idxs), name='DONE', index=idxs)
            col_done_by = pd.Series([worker]*len(idxs), name='DONE_BY', index=idxs)
            
            jobList.update(col_done)
            jobList.update(col_done_by)
            
            #print(jobList.head)
            
        ret_dict = {}

        ret_dict['JOB_LIST'] = ret_job_id

        ret_dict['JOB_RESULT'] = {}

        for rj,rp,rits, rwks in zip(ret_job_id, ret_coords, ret_job_items, ret_workers):

            ret_dict['JOB_RESULT'][rj] = {'ORDER_ITEM':rits,
                                        'WORKER':rwks,
                                        'PATH':rp}

        #print(ret_dict)
        return ret_dict



if __name__ == '__main__':

    ia = ItemAttribute()
    ia.ItemAttb

    orders = []

    random.seed(11) # for reproductivity

    dest_cand = ['DOOR_(1,0)', 'DOOR_(4,0)', 'DOOR_(7,0)',
        'DOOR_(10,0)','DOOR_(13,0)','DOOR_(16,0)', 'DOOR_(19,0)',
        'DOOR_(22,0)','DOOR_(25,0)','DOOR_(28,0)']

    for i in range(50):
        
        dest = random.choices(dest_cand,k=1)[0]
        
        start = 0 + random.randrange(0, 180)
        due = start + random.randrange(80, 160)
        
        orders.append(methods.test_input_generation_randomly(dest, due, start))

    jm = JobManager(orders, ia.ItemAttb)

    wm = WorkerManager()

    wm.set_worker(Worker("WK_1","DOOR_(1,0)",1))
    wm.set_worker(Worker("WK_2","DOOR_(7,0)",1))
    wm.set_worker(Worker("WK_3","DOOR_(13,0)",1))
    wm.set_worker(Worker("WK_4","DOOR_(19,0)",1))
    wm.set_worker(Worker("WK_5","DOOR_(25,0)",1))

    wh = Warehouse()

    wh.set_grid_layout(30,49)

    wh.set_doors([(1,0), (4,0), (7,0), (10,0), (13,0), (16,0), (19,0), (22,0), (25,0), (28,0)])

    wh.set_shelves([(0,i) for i in range(2,47)], 'R')
    wh.set_shelves([(29,i) for i in range(2,47)], 'L')

    for x in [2+3*j for j in range(9)]:
        wh.set_shelves([(x,i) for i in range(2,24)], 'L')
        wh.set_shelves([(x,i) for i in range(25,47)], 'L')

        wh.set_shelves([(x+1,i) for i in range(2,47)], 'R')
        wh.set_shelves([(x+1,i) for i in range(25,47)], 'R')

    wh.build_layout()

    wh.get_layout_for_render()

    im = ItemManager()

    im.get_WH_shelf_node_list(wh)

    im.get_item_full_list(['table_1','table_2','table_3','desk_1','desk_2','desk_3','chair_1','chair_2','chair_3','footrest'])

    xx = [0,2,3,5,6,8,9,11,12,14,15,17,18,20,21,23,24,26,27]
    yy = [i for i in range(2, 24)] + [i for i in range(25, 46)]


    check_list = []

    random.seed(11)

    for i in range(50):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('table_1', 'SHELF_({},{})'.format(x,y))
                break

    for i in range(50):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('table_2', 'SHELF_({},{})'.format(x,y))
                break

                
    for i in range(50):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('table_3', 'SHELF_({},{})'.format(x,y))
                break


    for i in range(100):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('desk_1', 'SHELF_({},{})'.format(x,y))
                break

    for i in range(70):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('desk_2', 'SHELF_({},{})'.format(x,y))
                break
                
    for i in range(50):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('desk_3', 'SHELF_({},{})'.format(x,y))
                break
                

    for i in range(60):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('chair_1', 'SHELF_({},{})'.format(x,y))
                break           


    for i in range(30):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('footrest', 'SHELF_({},{})'.format(x,y))
                break     
                

    for i in range(250):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('chair_2', 'SHELF_({},{})'.format(x,y))
                break     

    for i in range(100):
        while True:
            x = random.randrange(0,len(xx))
            y = random.randrange(0, len(yy))
            x = xx[x]
            y = yy[y]
            if (x,y) not in check_list:
                check_list.append((x,y))
                im.replenish_item('chair_3', 'SHELF_({},{})'.format(x,y))
                break     

    sc4 = [i for i in range(36, 47)]
    sc3 = [i for i in range(25, 36)]
    sc2 = [i for i in range(13, 24)]
    sc1 = [i for i in range(2, 13)]

    wh.tmp_set_zone('D1', [], ['DOOR_(1,0)'])
    wh.tmp_set_zone('D2', [], ['DOOR_(4,0)'])
    wh.tmp_set_zone('D3', [], ['DOOR_(7,0)'])
    wh.tmp_set_zone('D4', [], ['DOOR_(10,0)'])
    wh.tmp_set_zone('D5', [], ['DOOR_(13,0)'])
    wh.tmp_set_zone('D6', [], ['DOOR_(16,0)'])
    wh.tmp_set_zone('D7', [], ['DOOR_(19,0)'])
    wh.tmp_set_zone('D8', [], ['DOOR_(22,0)'])
    wh.tmp_set_zone('D9', [], ['DOOR_(25,0)'])
    wh.tmp_set_zone('D10', [], ['DOOR_(28,0)'])
    wh.tmp_set_zone('Z1_4',['SHELF_(0,{})'.format(i) for i in sc4]+['SHELF_(2,{})'.format(i) for i in sc4], ['AISLE_(1,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z1_3',['SHELF_(0,{})'.format(i) for i in sc3]+['SHELF_(2,{})'.format(i) for i in sc3], ['AISLE_(1,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z1_2',['SHELF_(0,{})'.format(i) for i in sc2]+['SHELF_(2,{})'.format(i) for i in sc2]+['SHELF_(0,24)'], ['AISLE_(1,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z1_1',['SHELF_(0,{})'.format(i) for i in sc1]+['SHELF_(2,{})'.format(i) for i in sc1], ['AISLE_(1,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z2_4',['SHELF_(3,{})'.format(i) for i in sc4]+['SHELF_(5,{})'.format(i) for i in sc4], ['AISLE_(4,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z2_3',['SHELF_(3,{})'.format(i) for i in sc3]+['SHELF_(5,{})'.format(i) for i in sc3], ['AISLE_(4,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z2_2',['SHELF_(3,{})'.format(i) for i in sc2]+['SHELF_(5,{})'.format(i) for i in sc2], ['AISLE_(4,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z2_1',['SHELF_(3,{})'.format(i) for i in sc1]+['SHELF_(5,{})'.format(i) for i in sc1], ['AISLE_(4,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z3_4',['SHELF_(6,{})'.format(i) for i in sc4]+['SHELF_(8,{})'.format(i) for i in sc4], ['AISLE_(7,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z3_3',['SHELF_(6,{})'.format(i) for i in sc3]+['SHELF_(8,{})'.format(i) for i in sc3], ['AISLE_(7,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z3_2',['SHELF_(6,{})'.format(i) for i in sc2]+['SHELF_(8,{})'.format(i) for i in sc2], ['AISLE_(7,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z3_1',['SHELF_(6,{})'.format(i) for i in sc1]+['SHELF_(8,{})'.format(i) for i in sc1], ['AISLE_(7,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z4_4',['SHELF_(9,{})'.format(i) for i in sc4]+['SHELF_(11,{})'.format(i) for i in sc4], ['AISLE_(10,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z4_3',['SHELF_(9,{})'.format(i) for i in sc3]+['SHELF_(11,{})'.format(i) for i in sc3], ['AISLE_(10,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z4_2',['SHELF_(9,{})'.format(i) for i in sc2]+['SHELF_(11,{})'.format(i) for i in sc2], ['AISLE_(10,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z4_1',['SHELF_(9,{})'.format(i) for i in sc1]+['SHELF_(11,{})'.format(i) for i in sc1], ['AISLE_(10,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z5_4',['SHELF_(12,{})'.format(i) for i in sc4]+['SHELF_(14,{})'.format(i) for i in sc4], ['AISLE_(13,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z5_3',['SHELF_(12,{})'.format(i) for i in sc3]+['SHELF_(14,{})'.format(i) for i in sc3], ['AISLE_(13,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z5_2',['SHELF_(12,{})'.format(i) for i in sc2]+['SHELF_(14,{})'.format(i) for i in sc2], ['AISLE_(13,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z5_1',['SHELF_(12,{})'.format(i) for i in sc1]+['SHELF_(14,{})'.format(i) for i in sc1], ['AISLE_(13,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z6_4',['SHELF_(15,{})'.format(i) for i in sc4]+['SHELF_(17,{})'.format(i) for i in sc4], ['AISLE_(16,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z6_3',['SHELF_(15,{})'.format(i) for i in sc3]+['SHELF_(17,{})'.format(i) for i in sc3], ['AISLE_(16,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z6_2',['SHELF_(15,{})'.format(i) for i in sc2]+['SHELF_(17,{})'.format(i) for i in sc2], ['AISLE_(16,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z6_1',['SHELF_(15,{})'.format(i) for i in sc1]+['SHELF_(17,{})'.format(i) for i in sc1], ['AISLE_(16,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z7_4',['SHELF_(18,{})'.format(i) for i in sc4]+['SHELF_(20,{})'.format(i) for i in sc4], ['AISLE_(19,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z7_3',['SHELF_(18,{})'.format(i) for i in sc3]+['SHELF_(20,{})'.format(i) for i in sc3], ['AISLE_(19,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z7_2',['SHELF_(18,{})'.format(i) for i in sc2]+['SHELF_(20,{})'.format(i) for i in sc2], ['AISLE_(19,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z7_1',['SHELF_(18,{})'.format(i) for i in sc1]+['SHELF_(20,{})'.format(i) for i in sc1], ['AISLE_(19,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z8_4',['SHELF_(21,{})'.format(i) for i in sc4]+['SHELF_(23,{})'.format(i) for i in sc4], ['AISLE_(22,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z8_3',['SHELF_(21,{})'.format(i) for i in sc3]+['SHELF_(23,{})'.format(i) for i in sc3], ['AISLE_(22,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z8_2',['SHELF_(21,{})'.format(i) for i in sc2]+['SHELF_(23,{})'.format(i) for i in sc2], ['AISLE_(22,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z8_1',['SHELF_(21,{})'.format(i) for i in sc1]+['SHELF_(23,{})'.format(i) for i in sc1], ['AISLE_(22,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z9_4',['SHELF_(24,{})'.format(i) for i in sc4]+['SHELF_(26,{})'.format(i) for i in sc4], ['AISLE_(25,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z9_3',['SHELF_(24,{})'.format(i) for i in sc3]+['SHELF_(26,{})'.format(i) for i in sc3], ['AISLE_(25,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z9_2',['SHELF_(24,{})'.format(i) for i in sc2]+['SHELF_(26,{})'.format(i) for i in sc2], ['AISLE_(25,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z9_1',['SHELF_(24,{})'.format(i) for i in sc1]+['SHELF_(26,{})'.format(i) for i in sc1], ['AISLE_(25,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z10_4',['SHELF_(27,{})'.format(i) for i in sc4]+['SHELF_(29,{})'.format(i) for i in sc4], ['AISLE_(28,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z10_3',['SHELF_(27,{})'.format(i) for i in sc3]+['SHELF_(29,{})'.format(i) for i in sc3], ['AISLE_(28,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z10_2',['SHELF_(27,{})'.format(i) for i in sc2]+['SHELF_(29,{})'.format(i) for i in sc2], ['AISLE_(28,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z10_1',['SHELF_(27,{})'.format(i) for i in sc1]+['SHELF_(29,{})'.format(i) for i in sc1] + ['SHELF_(29,24)'], ['AISLE_(28,{})'.format(i) for i in sc1])
    wh.tmp_abstract_graph()

    wh.set_zone_counter(im)
    zc =wh.zone_counter

    pp = Plan(wh, wm, jm, im)


    aplan = pp.do_plan_assignment()

    print(json.dumps(aplan))