

import itertools
import random
import networkx as nx
import json
import collections
from order import Order

random.seed(11)

def find_all_adj(G, zone_list):
    
    ret_temp = []
    ret_final = []
    from_zone = zone_list[-1]
    
    adj = nx.all_neighbors(G,from_zone)

    for adj_i in adj:

        if "D" not in adj_i:
            ret_temp.append(zone_list + [adj_i])
        
    for r in ret_temp:
        # check for meaningless cycle
        if len(set(r)) == len(r) :
            ret_final.append(r)
        
    return ret_final


def check_fullfilment(zc, zone_list, orders):

    
    zcnt = collections.Counter()
    ocnt = collections.Counter(orders)

    for z in zone_list:
        
        if 'D' not in z:
            zcnt = zcnt + zc[z]
    
    remain = ocnt - zcnt
    remain = remain - collections.Counter()

    if remain == collections.Counter():
        return True
    else :
        return False
    

def dive_in(G, zc, origin, destination, orders, threshold=100):
    
    bag = []
    
    candidate = [[origin]]
    
    count = 30


    while len(bag) < 5 and count > 0:
        
        candidate_branched = []
        
        for cd in candidate:
            adjs = find_all_adj(G, cd)
            for a in adjs:
                if check_fullfilment(zc, a, orders) :
                    bag.append(a)
                else:
                    candidate_branched.append(a)
                    
        candidate = candidate_branched
        count -= 1
    
    ret = []

    for b in bag:
        
        pp = nx.shortest_path(G, b[-1], destination)
        ret.append(b[:-1] + pp)

    # print('Dive_IN RET:', ret)
    min_sum_weight = 100000000
    shortest_path = None

    paths = []

    for r in ret:
        sum_weight = 0
        
        for n1, n2 in zip(r[:-1], r[1:]):
            sum_weight += G.get_edge_data(n1,n2,'weight')['weight']
        if sum_weight < min_sum_weight:
            min_sum_weight = sum_weight
            shortest_path = r

        paths.append((sum_weight*1.1 + 4, r))

    return_paths = []

    for ps in paths:

        if ps[0] <= min_sum_weight + threshold :
            return_paths.append(ps)

    return return_paths

def sort_visit(WH, abstract_from, abstract_to, node_to_visit):
    
    (fx, fy) = WH.zones[abstract_from]['CENTER']
    (tx, ty) = WH.zones[abstract_to]['CENTER']
    
    coords=nx.get_node_attributes(WH.WH_graph,'coords')
    
    if WH.zones[abstract_to]['ZONE_TYPE'] == 'V' :
        if fy > ty:
            # DESC y 
            return sorted(node_to_visit, key= lambda x: coords[x][1], reverse=True)
        elif fy == ty:
            if WH.zones[abstract_to]['TIE_APPROACH'] == 'UD':
                # DESC y
                return sorted(node_to_visit, key= lambda x: coords[x][1], reverse=True)
            else:
                # ASC y
                return sorted(node_to_visit, key= lambda x: coords[x][1], reverse=False)
        else :
            # ASC y
            return sorted(node_to_visit, key= lambda x: coords[x][1], reverse=False)
    else :
        if fx > tx:
            # DESC y 
            return sorted(node_to_visit, key= lambda x: coords[x][0], reverse=True)
        elif fx == tx:
            if WH.zones[abstract_to]['TIE_APPROACH'] == 'RL':
                # DESC x
                return sorted(node_to_visit, key= lambda x: coords[x][0], reverse=True)
            else:
                # ASC x
                return sorted(node_to_visit, key= lambda x: coords[x][0], reverse=False)
        else :
            # ASC x
            return sorted(node_to_visit, key= lambda x: coords[x][0], reverse=False)
        


def get_detail_and_consume(WH, zc, abstract_path, order, im):
    
    ocnt = collections.Counter(order)
    
    outerbag = []
    
    target = abstract_path[1:-1]
    target.reverse()
    
    origin = WH.zones[abstract_path[0]]['AISLE'][0]
    dest = WH.zones[abstract_path[-1]]['AISLE'][0]
    
    for i, zone in enumerate(target):

        usable = zc[zone] & ocnt
        shelf = set(WH.zones[zone]['SHELF'])
        
        node_to_be_visit = []
        #print(zone, usable)
        for key in usable:
            item = set(im.items[key])
            intersection = list(shelf & item)
            intersection = intersection[:usable[key]]
            node_to_be_visit = node_to_be_visit + intersection
            
            for ii in intersection:
                im.consume_item(key, ii)
                
                # print(key, 'is consumed from ',ii)
                
                ocnt[key] -= 1
            #print(len(im.items[key]))
        
        ocnt = ocnt - collections.Counter()
        # print(ocnt)  
        zc[zone] -= usable
        
        outerbag.append(node_to_be_visit)
            
            
    outerbag.reverse()
    target.reverse()
    
    ret = []
    
    for i, nodes in enumerate(outerbag):
        
        if i==0:
            ret = ret+[origin]
            ret = ret + sort_visit(WH, abstract_path[0],  target[i], nodes)

        else :
            
            ret = ret + sort_visit(WH,  target[i-1], target[i], nodes)

        if i == len(outerbag) - 1:

            # ret = ret + sort_visit(WH, target[i], abstract_path[-1], nodes)
            ret = ret + [dest]
            
    return ret

def find_path(G, IM, node_to_visit):
    
    ret_path = []
    
    for s,t in zip(node_to_visit[:-1], node_to_visit[1:]):
       
        if s==t:
            print(s,t, ret_path)
            ret_path = ret_path + [ret_path[-2], t]
            
        else :
            path = nx.shortest_path(G, source = s, target = t ,weight ='weight')
            ret_path = ret_path[:-1] + path
    
    ret = []
    
    for node in ret_path:
        
        if 'SHELF' in node:
            ret.append((node, IM.consumed_item[node]))
        else :
            ret.append((node,''))
    
    
    IM.clear_consumed_item()
    
    return ret


def path2Coords(G, path, startingTimeOffset):

    ret = []
    cur = startingTimeOffset
    coords=nx.get_node_attributes(G,'coords')
    ret = []
    
    item_holding = collections.Counter()
    cur_holding = collections.Counter()
    
    time_consumed = 0
    
    for n1, n2 in zip(path[:-1], path[1:]):
        
        u = n1[0]
        v = n2[0]
        
        cur_holding = item_holding.copy()
        
        check = False
        if n2[1] != '':
            item_holding[n2[1]] += 1
            check = True
        
        
        it_ = dict(cur_holding)
        
        ret.append({'from':coords[u], 'to':coords[v], 'duration':G[u][v]['weight'], 'current':cur, 'item_holding':it_, 'grab_item':check})
        cur = cur + G[u][v]['weight']
        time_consumed += G[u][v]['weight']
    
    
    return ret, time_consumed












