import pandas as pd

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
        
    def use_item(self, item, useFrom):
        
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
