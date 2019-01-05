class ItemManager:
    
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
        use_item = self.shelves[useFrom].index(item)
        del self.shelves[useFrom][use_item]
        
        use_from = self.items[item].index(useFrom)
        del self.items[item][use_from]