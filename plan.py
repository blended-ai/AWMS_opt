from copy import deepcopy
import random
import methods
import pandas as pd

import pickle
import os.path
#import collections

#from itemmanager import ItemManager
from itemmanager import ItemAttribute
import itemmanager
#from workermanager import WorkerManager
#from workermanager import Worker
import workermanager
from jobmanager import JobManager
import order
#from warehouse import Warehouse
import warehouse
import json

from tqdm import tqdm

class Plan:

    class PlanStats:

        def __init__(self, JobDf, workerManager):

            df = deepcopy(JobDf)
            df_max_late = df.groupby(['ORDER_ID']).agg({'DONE':'max', 'DUE':'max'})

            df_max_late['GAP'] = df_max_late['DONE'] - df_max_late['DUE']

            self.job_df = JobDf
            self.num_order = len(df_max_late)
            self.max_late = max(df_max_late['GAP'].values)
            self.sum_late = sum(df_max_late[df_max_late['GAP'] > 0]['GAP'].values)
            if df_max_late[df_max_late['GAP'] > 0].empty:
                self.num_late = 0
            else :
                self.num_late = len(df_max_late[df_max_late['GAP'] > 0].values)

            self.avg_late = self.sum_late/self.num_order
            self.avg_late2 = self.sum_late/self.num_late if self.num_late > 0 else 0

            sum_travel_time = 0
            sum_waste_time = 0

            workers = deepcopy(workerManager.workers)

            for w in workers:
                sum_travel_time += workers[w].travel
                sum_waste_time += (workers[w].last_job_done_at - workers[w].travel)

            self.sum_travel_time = sum_travel_time
            self.sum_waste_time = sum_waste_time



    def __init__(self, WH, workerManager, jobManager, itemManager):

        self.original_itemManager = itemManager
        self.original_jobManager = jobManager
        self.original_workerManager = workerManager
        self.original_wareHouse = WH

    def get_next_job(self, jobList):

        target = jobList[jobList['DONE'] == -1]

        if len(target) > 0:
            target_id = target.iloc[0]['JOB_ID']

            target = target[target['JOB_ID'] == target_id]
            dest = target.iloc[0]['DEST']
            start_from = max(target['START'])
            earliest_due = min(target['DUE'])
            idxs = target.index

            # print(target_id)
            # print(target)

            return list(target['ITEM'].values), dest, start_from, idxs, earliest_due
        else :
            return [], 'a','b',[], 'c'


    def do_plan_assignment2(self):

        itemM = deepcopy(self.original_itemManager)
        jobM = deepcopy(self.original_jobManager)
        workerM = deepcopy(self.original_workerManager)
        wareH = deepcopy(self.original_wareHouse)
        # print(len(itemM.items), len(itemM.shelves))
        done = False

        jobList = jobM.policyJobByOrder()
        # print(jobList)
        jobList['DONE'] = -1
        jobList['DONE_BY'] = ''

        ret_coords = []
        ret_order_id = []
        ret_job_id = []
        ret_job_items = []
        ret_workers = []

        cur_time = 0

        while not done:

            # print(worker_candidates)

            worker_candidates = []

            job, dest, start, idxs, earliest_due = self.get_next_job(jobList)

            if len(job) < 1:
                break

            if dest in ['DOOR_(1,0)','DOOR_(4,0)', 'DOOR_(7,0)']:
                worker_candidates.append(('WK_1', workerM.workers['WK_1'].on_from))
            if dest in ['DOOR_(4,0)', 'DOOR_(7,0)','DOOR_(10,0)', 'DOOR_(13,0)']:
                worker_candidates.append(('WK_2', workerM.workers['WK_2'].on_from))
            if dest in ['DOOR_(10,0)','DOOR_(13,0)','DOOR_(16,0)','DOOR_(19,0)']:
                worker_candidates.append(('WK_3', workerM.workers['WK_3'].on_from))
            if dest in ['DOOR_(16,0)','DOOR_(19,0)','DOOR_(22,0)','DOOR_(25,0)']:
                worker_candidates.append(('WK_4', workerM.workers['WK_4'].on_from))
            if dest in ['DOOR_(22,0)','DOOR_(25,0)','DOOR_(28,0)']:
                worker_candidates.append(('WK_5', workerM.workers['WK_5'].on_from))


            pool = []
            least_best = None
            for wc in worker_candidates:

                origin_zone = wareH.zone_door_map[workerM.workers[wc[0]].pos]
                dest_zone = wareH.zone_door_map[dest]

                abstract_path_candidates = methods.dive_in(wareH.WH_abstract_graph, wareH.zone_counter, origin_zone, dest_zone, job)

                for pc in abstract_path_candidates:

                    time_ = pc[0] + wc[1] + len(job) * 8

                    if time_ < earliest_due:
                        pool.append((wc[0], wc[1], pc[1], time_, earliest_due-time_))

                if least_best is None:
                    least_best = (wc[0], wc[1], pc[1])
                else:
                    if least_best[1] > wc[1]:
                        least_best = (wc[0], wc[1], pc[1])
            # print(jobList.loc[idxs[0]]['JOB_ID'])
            # print(worker, job, p, m)

            if len(pool) > 0:
                # print(pool)
                pool = sorted(pool, key=lambda x: x[3])
                choice = pool[0]

            else:
                choice = least_best

            worker, cur_time, p = choice[0], choice[1], choice[2]

            result = methods.get_detail_and_consume(wareH, wareH.zone_counter, p, job, itemM)
            fp = methods.find_path(wareH.WH_graph, itemM, result)

            route, consumed_time = methods.path2Coords(wareH.WH_graph, fp, cur_time)

            ret_coords.append(route)
            ret_job_id.append(jobList.loc[idxs[0]]['JOB_ID'])
            t_orders = list(jobList.loc[idxs]['ORDER_ID'].values)
            t_items = list(jobList.loc[idxs]['ITEM'].values)

            sub_ = []
            for to, ti in zip(t_orders, t_items):
                sub_.append((to, ti))

            # ret_job_items.append(job)
            ret_job_items.append(sub_)
            ret_workers.append(worker)

            so_time = max(consumed_time + cur_time, start)

            workerM.workers[worker].on_from = so_time
            workerM.workers[worker].pos = dest
            workerM.workers[worker].travel += consumed_time
            workerM.workers[worker].wait += 0 if start < consumed_time + cur_time else start - cur_time - consumed_time
            workerM.workers[worker].job_done += 1
            workerM.workers[worker].last_job_done_at = so_time

            col_done = pd.Series([so_time] * len(idxs), name='DONE', index=idxs)
            col_done_by = pd.Series([worker] * len(idxs), name='DONE_BY', index=idxs)

            jobList.update(col_done)
            jobList.update(col_done_by)

            # print(jobList.head)

            ret_dict = {}

            ret_dict['JOB_LIST'] = ret_job_id

            ret_dict['JOB_RESULT'] = {}

            for rj, rp, rits, rwks in zip(ret_job_id, ret_coords, ret_job_items, ret_workers):
                ret_dict['JOB_RESULT'][rj] = {'ORDER_ITEM': rits,
                                              'WORKER': rwks,
                                              'PATH': rp}

            a_ps = self.PlanStats(jobList, workerM)

        return (deepcopy(ret_dict), deepcopy(a_ps))

    def do_plan_assignment(self):

        min_max_late_plan_stats = None
        min_avg_late_plan_stats = None
        min_avg_late2_plan_stats = None
        min_num_late_plan_stats = None
        min_travel_time_plan_stats = None

        min_max_late_plan = None
        min_avg_late_plan = None
        min_avg_late2_plan = None
        min_num_late_plan = None
        min_travel_time_plan = None

        min_max_late = 1000000
        min_avg_late = 1000000
        min_avg_late2 = 1000000
        min_num_late = 1000000
        min_travel_time = 10000000

        iter = 10

        pbar = tqdm(total=100)

        for _ in range(iter):

            itemM = deepcopy(self.original_itemManager)
            jobM = deepcopy(self.original_jobManager)
            workerM = deepcopy(self.original_workerManager)
            wareH = deepcopy(self.original_wareHouse)
            # print(len(itemM.items), len(itemM.shelves))
            done = False

            jobList = jobM.policyJobByOrder()
            # print('\n',jobList)
            jobList['DONE'] = -1
            jobList['DONE_BY'] = ''

            ret_coords = []
            ret_order_id = []
            ret_job_id = []
            ret_job_items = []
            ret_workers = []

            cur_time = 0

            job_size = len(jobList['JOB_ID'].unique())

            ud = 100 / iter / job_size

            while not done:

                worker_candidates = workerM.get_next_on()

                # print(worker_candidates)
                job, dest, start, idxs, earliest_due = self.get_next_job(jobList)

                if len(job) < 1:
                    break

                pool = []
                least_best = None
                # print('\n',job, start, earliest_due, worker_candidates)

                for wc in worker_candidates:

                    origin_zone = wareH.zone_door_map[workerM.workers[wc[0]].pos]
                    dest_zone = wareH.zone_door_map[dest]

                    abstract_path_candidates = methods.dive_in(wareH.WH_abstract_graph, wareH.zone_counter, origin_zone,
                                                               dest_zone, job)
                    for pc in abstract_path_candidates:

                        time_ = pc[0] + wc[1] + len(job) * 8

                        if time_ * 1.2 < earliest_due:
                            pool.append((wc[0], wc[1], pc[1], time_, earliest_due - time_))

                        if least_best is None:
                            least_best = (wc[0], wc[1], pc[1])
                        else:
                            if least_best[1] > wc[1]:
                                least_best = (wc[0], wc[1], pc[1])
                    # print(jobList.loc[idxs[0]]['JOB_ID'])
                    # print(worker, job, p, m)

                if len(pool) > 0:

                    pool = sorted(pool, key=lambda x: x[3])
                    pool2 = pool[:3]
                    choice = random.choices(pool2, k=1)[0]
                    # print('among', pool2)
                    # print('adaptable best', choice)
                else:
                    # print('least worst', least_best)
                    choice = least_best

                worker, cur_time, p = choice[0], choice[1], choice[2]

                result = methods.get_detail_and_consume(wareH, wareH.zone_counter, p, job, itemM)
                fp = methods.find_path(wareH.WH_graph, itemM, result)

                route, consumed_time = methods.path2Coords(wareH.WH_graph, fp, cur_time)

                ret_coords.append(route)
                ret_job_id.append(jobList.loc[idxs[0]]['JOB_ID'])
                t_orders = list(jobList.loc[idxs]['ORDER_ID'].values)
                t_items = list(jobList.loc[idxs]['ITEM'].values)

                sub_ = []
                for to, ti in zip(t_orders, t_items):
                    sub_.append((to, ti))

                # ret_job_items.append(job)
                ret_job_items.append(sub_)
                ret_workers.append(worker)

                so_time = max(consumed_time + cur_time, start)

                workerM.workers[worker].on_from = so_time
                workerM.workers[worker].pos = dest
                workerM.workers[worker].travel += consumed_time
                workerM.workers[worker].wait += 0 if start < consumed_time + cur_time else start - cur_time - consumed_time
                workerM.workers[worker].job_done += 1
                workerM.workers[worker].last_job_done_at = so_time

                # print(worker, 'completed at', so_time, '(', consumed_time , '+', 0 if start < consumed_time + cur_time else start - cur_time - consumed_time, ')')
                col_done = pd.Series([so_time] * len(idxs), name='DONE', index=idxs)
                col_done_by = pd.Series([worker] * len(idxs), name='DONE_BY', index=idxs)

                jobList.update(col_done)
                jobList.update(col_done_by)

                pbar.update(ud)

                    # print(jobList.head)

            ret_dict = {}

            ret_dict['JOB_LIST'] = ret_job_id

            ret_dict['JOB_RESULT'] = {}

            for rj, rp, rits, rwks in zip(ret_job_id, ret_coords, ret_job_items, ret_workers):
                ret_dict['JOB_RESULT'][rj] = {'ORDER_ITEM': rits,
                                              'WORKER': rwks,
                                              'PATH': rp}

            # for wk in workerM.workers:
            #
            #     this_worker = workerM.workers[wk]
            #     print(this_worker.id, this_worker.travel, this_worker.wait,  this_worker.job_done)

            a_ps = self.PlanStats(jobList, workerM)
            if a_ps.max_late < min_max_late:
                min_max_late = a_ps.max_late
                min_max_late_plan = deepcopy(ret_dict)
                min_max_late_plan_stats = deepcopy(a_ps)

            if a_ps.avg_late < min_avg_late:
                min_avg_late = a_ps.avg_late
                min_avg_late_plan = deepcopy(ret_dict)
                min_avg_late_plan_stats = deepcopy(a_ps)

            if a_ps.avg_late2 < min_avg_late2:
                min_avg_late2 = a_ps.avg_late2
                min_avg_late2_plan = deepcopy(ret_dict)
                min_avg_late2_plan_stats = deepcopy(a_ps)

            # if a_ps.sum_travel_time < min_travel_time:
            #     min_travel_time = a_ps.sum_travel_time
            #     min_travel_time_plan = deepcopy(ret_dict)
            #     min_travel_time_plan_stats = deepcopy(a_ps)

        # print(ret_dict)
        pbar.close()
        return (min_max_late_plan, min_max_late_plan_stats) , \
               (min_avg_late_plan, min_avg_late_plan_stats), \
               (min_avg_late2_plan, min_avg_late2_plan_stats)


if __name__ == '__main__':

    ia = ItemAttribute()
    ia.ItemAttb

    orders = []

    if os.path.exists("./orders1_seed_11.txt") :
        print('Get Orders from ./orders1_seed_11.txt')
        with open('./orders1_seed_11.txt', 'rb') as f:
            data = pickle.load(f)
        orders = data
    else :
        print('Generate Orders into ./orders1_seed_11.txt')
        order.gen_test_order('orders1_seed_11.txt')
        with open('./orders1_seed_11.txt', 'rb') as f:
            data = pickle.load(f)
        orders = data

    jm = JobManager(orders, ia.ItemAttb)

    wm = workermanager.gen_test_workerManager()

    wh = warehouse.gen_test_wh_layout()

    wh_layout = wh.get_layout_for_render()

    if os.path.exists("./items.txt") :
        print('Get Items from ./items.txt')
        with open('./items.txt', 'rb') as f:
            data = pickle.load(f)
        im = data
    else :
        print('Generate Items into ./items.txt')
        itemmanager.gen_test_items(orders, wh, 'items.txt')
        with open('./items.txt', 'rb') as f:
            data = pickle.load(f)
        im = data

    wh = warehouse.gen_test_zone(wh, im)

    pp = Plan(wh, wm, jm, im)

    comparePlan = pp.do_plan_assignment2()
    print('\nREFERENCE')
    print('max_late:', comparePlan[1].max_late)
    print('avg_late:', comparePlan[1].avg_late)
    print('avg_late2:', comparePlan[1].avg_late2)
    print('num_late:', comparePlan[1].num_late)
    print('sum_travel:', comparePlan[1].sum_travel_time)
    print('sum_waste_time:', comparePlan[1].sum_waste_time)

    with open('REFERENCE_plan.json', 'w') as outfile:
        json.dump(comparePlan[0], outfile)

    aplan, bplan, cplan = pp.do_plan_assignment()
    name = ['min_max_late','min_avg_late','min_avg_late2']

    for pl,n in zip([aplan, bplan, cplan], name):
        print('')
        print(n)
        print('max_late:', pl[1].max_late)
        print('avg_late:', pl[1].avg_late)
        print('avg_late2:', pl[1].avg_late2)
        print('num_late:', pl[1].num_late)
        print('sum_travel:', pl[1].sum_travel_time)
        print('sum_waste_time:', pl[1].sum_waste_time)

        with open(n+'_plan.json','w') as outfile:
            json.dump(pl[0], outfile)


