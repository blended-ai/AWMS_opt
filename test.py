from itemmanager import ItemManager
from order import Order
from warehouse import Warehouse
import itertools
import random
import networkx as nx
import json

def pathFind(G, orderItemKeys, starting_points, destination, itemset):
    
    """
    orderItemKeys: list of keys used to retieve the pos of items by using dict
    starting_points: list of node names which is used to picker's starting points.
    destination: order's destination node name, assume single destination only..
    
    """
    order_perm = list(itertools.permutations(orderItemKeys))

    minC = 10000
    bag = []
    # assume that dict dd is already created
    for op in order_perm:
        toFind = [starting_points]
        for perm in op:
            toFind.append(list(set(itemset[perm])))
        toFind.append([destination])
        
        order_cands = list(itertools.product(*toFind))
        for oc in order_cands:
            
            path = []
            for fr, to in zip(oc[:-1],oc[1:]):
                path.append(nx.shortest_path(G, source=fr, target = to))
            
            count = 0
            count = sum([len(x) for x in path])

            if count < minC :
                minC = count
                bag= []
                
                for p in path:
                    bag.append(p)
    return bag

def path2(G, path, startingTime):
    
    """
    return list of tuples 
    each tuple has (from xy, to xy, length, starting time) 
    """
    ret = []
    cur = startingTime
    coords=nx.get_node_attributes(G,'coords')
    ret = []
    for subpath in path:
        
        subret = []
        for u, v in zip(subpath[:-1], subpath[1:]):
            subret.append((coords[u],coords[v],G[u][v]['weight'], cur))
            cur = cur + G[u][v]['weight']        
        ret = ret + subret
        
    return ret

def test_input_dependency_generation(item, prob):
    # 대략적으로 의자 1는 발받침과 함께 쓸 수 있는 의자,
    # 의자 2는 책상과 함께 쓸 수 있는 의자
    # 의자 3는 탁자용 의자라고 하자!

    # 물론 아무 상관 없이 들어올 수도 있다.
    
    supplementary = []
    
    if 'table' in item:
        supplementary = ['chair_2'] * random.randrange(1,5)
    elif 'desk' in item:
        supplementary = ['chair_3']
    elif 'chair_1' in item:
        supplementary = ['footrest']
    
    if random.random() < prob:
        
        return [item] + supplementary
    
    else :
        return [item]
        

def test_input_generation_randomly(dest, due, start):
    # 탁자 1, 2, 3 의 선호도는 각각 6:3:1
    # 책상 1, 2, 3 의 선호도는 각각 5:4:1
    
    itemset = []
    
    tableR = random.random()
    
    if  tableR > 0.6 :
        itemset = itemset + test_input_dependency_generation('table_1',0.7)
    elif tableR > 0.1 :
        itemset = itemset + test_input_dependency_generation('table_2',0.7)
    else :
        itemset = itemset + test_input_dependency_generation('table_3',0.7)  
    
    deskR = random.random()
    if  deskR > 0.5 :
        itemset = itemset + test_input_dependency_generation('desk_1',0.3)
    elif deskR > 0.1 :
        itemset = itemset + test_input_dependency_generation('desk_2',0.3)
    else :
        itemset = itemset + test_input_dependency_generation('desk_3',0.3)  
        
    chairR = random.random() 
    if  chairR > 0.8 :
        itemset = itemset + test_input_dependency_generation('chair_1',0.5)
    
    chairR = random.random() 
    if  chairR > 0.8 :
        itemset = itemset + test_input_dependency_generation('chair_2',0.5)
        
    chairR = random.random() 
    if  chairR > 0.8 :
        itemset = itemset + test_input_dependency_generation('chair_3',0.5)
    
    return Order(itemset, dest, due, start)



if __name__ == "__main__":

    orders = []

    for i in range(10):
        
        dest = 'DOOR_(0,0)'
        if random.random() > 0.6:
            dest = 'DOOR_(4,0)'
        
        due = 200 + random.randrange(-30, 120)
        start = due - 100 + random.randrange(0, 60)
        
        orders.append(test_input_generation_randomly(dest, due, start))
        
    # for o in orders:
    #     print(sorted(o.items), o.dest, o.start, o.due)
    wh = Warehouse()

    wh.set_grid_layout(5,10)

    wh.set_doors([(0,0), (4,0)])

    wh.set_shelves([(1,1),(2,1),(3,1),(1,3),(2,3),(3,3),(1,5),(2,5),(3,5),(1,7),(2,7),(3,7)], 'D')

    wh.set_blocks([(0,9),(4,9)])

    wh.build_layout()
    im = ItemManager()

    im.get_WH_shelf_node_list(wh)

    im.get_item_full_list(['table_1','table_2','table_3','desk_1','desk_2','desk_3','chair_1','chair_2','chair_3','footrest'])


    for i in range(10):
        im.replenish_item('table_1', 'SHELF_(1,1)')
        im.replenish_item('table_2', 'SHELF_(1,3)')
        im.replenish_item('table_3', 'SHELF_(1,7)')
        
        im.replenish_item('desk_1', 'SHELF_(2,1)')
        im.replenish_item('desk_2', 'SHELF_(2,3)')
        im.replenish_item('desk_3', 'SHELF_(2,5)')
        

    for i in range(10):
        
        im.replenish_item('chair_1', 'SHELF_(3,1)')
        im.replenish_item('footrest', 'SHELF_(3,3)')
        im.replenish_item('chair_2', 'SHELF_(1,5)')
        im.replenish_item('chair_2', 'SHELF_(3,5)')
        im.replenish_item('chair_2', 'SHELF_(2,7)')
        im.replenish_item('chair_3', 'SHELF_(3,7)')

    orderOperationDict = {}
    orderOperationDict['ORDERS'] = []

    p1 = pathFind(wh.WH_graph, orders[0].items, ['DOOR_(0,0)'], orders[0].dest, im.items)
    orderOperationDict[orders[0].id] = path2(wh.WH_graph, p1, 0)
    orderOperationDict['ORDERS'].append(orders[0].id)

    p2 = pathFind(wh.WH_graph, orders[1].items, ['DOOR_(4,0)'], orders[1].dest, im.items)
    orderOperationDict[orders[1].id] = path2(wh.WH_graph, p2, 0)
    orderOperationDict['ORDERS'].append(orders[1].id)

    p3 = pathFind(wh.WH_graph, orders[2].items, ['DOOR_(0,0)'], orders[2].dest, im.items)
    orderOperationDict[orders[2].id] = path2(wh.WH_graph, p3, 0)
    orderOperationDict['ORDERS'].append(orders[2].id)

    print(json.dumps(orderOperationDict))