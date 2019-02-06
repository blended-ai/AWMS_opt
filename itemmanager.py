import pandas as pd
import random
import collections
import pickle

class ItemManager:
    
    def __init__(self):
        self.consumed_item = {}
        
    def clear_consumed_item(self):
        self.consumed_item = {}

    def get_WH_shelf_node_list(self, wh):        
        snodes = {}
        for s in wh.WH_shelf_node_list:
            snodes[s] = []
        
        self.shelves = snodes
    
    def get_item_full_list(self, lst):
        item_list = list(set(lst))
        imaps = {}
        for i in item_list:
            imaps[i] = []
        self.items = imaps
        
    
    def check_capacity(self):
        pass
    
    def check_availability(self):
        pass
    
    def replenish_item(self, item, addTo):
        
        # check capacity first!
        self.shelves[addTo].append(item)
        self.items[item].append(addTo)
        
    def consume_item(self, item, useFrom):
        
        # check availability fisrt!
        self.consumed_item[useFrom] = item
        use_item = self.shelves[useFrom].index(item)
        del self.shelves[useFrom][use_item]
        
        use_from = self.items[item].index(useFrom)
        del self.items[item][use_from]


class ItemAttribute:
    
    """ Temporal for Demo """
    def __init__(self):
        # temporal
        
        item = ['desk_1', 'desk_2', 'desk_3', 
                'table_1','table_2','table_3',
                'chair_1','chair_2','chair_3',
                'footrest']
        vol = [10, 10, 10,
               15, 15, 15,
               3, 3, 3,
               3]
        
        self.ItemAttb = pd.DataFrame.from_dict({'ITEM':item,'VOL':vol})

def gen_test_items(orders, wh, name):

    im = ItemManager()

    im.get_WH_shelf_node_list(wh)

    full_list = ['table_1', 'table_2', 'table_3',
                 'desk_1', 'desk_2', 'desk_3',
                 'chair_1', 'chair_2', 'chair_3',
                 'footrest']

    im.get_item_full_list(full_list)

    xx = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 23, 24, 26, 27]
    yy = [i for i in range(2, 24)] + [i for i in range(25, 46)]

    all_items = []

    for o in orders:
        all_items = all_items + o.items

    ic = collections.Counter(all_items)

    unoccupied = []
    for x in xx:
        for y in yy:
            unoccupied.append((x, y))


    mult = len(unoccupied) / sum(ic.values())

    if mult < 1:

        "************************REPLENISH ITEMS FIRST!!!!!!!!!!!!!!*********************"
    else:
        if mult * 0.8 > 1:
            mult = mult * 0.8
        else:
            mult = mult

    for each_item in full_list:

        for i in range(int(ic[each_item] * mult)):
            random.shuffle(unoccupied)
            x = unoccupied[0][0]
            y = unoccupied[0][1]
            im.replenish_item(each_item, 'SHELF_({},{})'.format(x, y))

            unoccupied = unoccupied[1:]

        print(each_item, '\nOrdered: ', ic[each_item], '\nReplenished: ', len(im.items[each_item]))

    with open('./' + name, 'wb') as f:
        pickle.dump(im, f)
