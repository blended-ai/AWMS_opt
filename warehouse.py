import networkx as nx
import collections 
from copy import deepcopy

class Warehouse:
    
    def __init__(self):
        self.aisle_form = lambda x,y: "AISLE_({},{})".format(str(x),str(y)) 
        self.shelf_form = lambda x,y: "SHELF_({},{})".format(str(x),str(y))
        self.door_form = lambda x,y: "DOOR_({},{})".format(str(x),str(y))
        self.block_form = lambda x,y: "BLOCK_({},{})".format(str(x),str(y))
        
        # parameterize this!
        self.aisle_to_shelf_weight = 4
        self.aisle_to_aisle_weight = 1
        self.aisle_to_door_weight = 2
        self.zones = {}
        self.zone_door_map = {}
    
    def xy_to_ij(self, x, y):
        return self.WH_height-1-y, x
    
    def ij_to_xy(self, i,j):
        return j,self.WH_height-1-i
    
    def get_adj_nodes(self, i,j): 
        cands = [(i-1,j), (i+1,j), (i, j-1), (i,j+1)]
        target = []
        for c in cands:
            if -1 < c[0] < self.WH_height and -1 < c[1] < self.WH_width:
                target.append(self.WH_grid[c[0]][c[1]])
        return target
    
    def link_row_wise(self):    
        conn=nx.get_node_attributes(self.WH_graph,'conn')       
        for r in self.WH_grid:            
            for left, right in zip(r[:-1], r[1:]):                
                if conn[left] in ('A', 'R','RL') and conn[right] in ('A','L','RL') and not ('SHELF' in left and 'SHELF' in right):                
                    weight_ = self.aisle_to_aisle_weight
                    if ('AISLE' in left and 'DOOR' in right) or ('DOOR' in left and 'AISLE' in right) :
                        weight_ = self.aisle_to_door_weight
                    elif ('AISLE' in left and 'SHELF' in right) or ('SHELF' in left and 'AISLE' in right) :
                        weight_ = self.aisle_to_shelf_weight
                    self.WH_graph.add_edge(left, right, weight=weight_)
                
    def link_column_wise(self):
        conn=nx.get_node_attributes(self.WH_graph,'conn')   
        for c in zip(*self.WH_grid):
            c = [*c]
            for up, down in zip(c[:-1], c[1:]):
                if (conn[up] in ('A', 'D','UD') and conn[down] in ('A','U','UD')) and not ('SHELF' in up and 'SHELF' in down) :           
                    weight_ = self.aisle_to_aisle_weight
                    if ('AISLE' in up and 'DOOR' in down) or ('DOOR' in up and 'AISLE' in down) :
                        weight_ = self.aisle_to_door_weight
                    elif ('AISLE' in up and 'SHELF' in down) or ('SHELF' in up and 'AISLE' in down) :
                        weight_ = self.aisle_to_shelf_weight
                    self.WH_graph.add_edge(up, down, weight=weight_)
    
    def set_grid_layout(self, width, height):
        """
        Args:
          width: width of grid layout (int).
          length: height of grid layout (int).
        Note:
          Only available for Rectangular grid layout.
          Using X, Y coordinates starting from 0.
          Diagonal movement is not allowed in the grid.
        """
        
        self.WH_width = width
        self.WH_height = height
        
        self.WH_grid = [[self.aisle_form(w, height-1-h) for w in range(width)] for h in range(height)]
        
        self.WH_graph = nx.Graph()
        self.WH_door_node_list = []
        self.WH_shelf_node_list = []
        self.WH_block_node_list = []
        self.WH_aisle_node_list = []
        
    
    def set_doors(self, pos):
        """
        Args:
          pos: list of (x,y) of each door way.
        Note:
          All doors should be positioned the boundary of grid.
        """
        
        for p in pos:
            i,j = self.xy_to_ij(*p)
            node_name = self.door_form(*p)
            self.WH_graph.add_node(node_name, coords = p, index=(i,j), node_type = "D" , conn='A')
            self.WH_door_node_list.append(node_name)
            
            self.WH_grid[i][j] = node_name
            
    def set_shelves(self, pos, conn):
        """
        Args:
          pos: list of (x,y) of each shelf.
          conn: direction of shelf face. One of {'A'(ll), 'L'(eft), 'R'(ight), 'U'(p), 'D'(own), 'LR', 'UD', 'N'(one)}.
        """
        
        for p in pos:
            i,j = self.xy_to_ij(*p)
            node_name = self.shelf_form(*p)
            self.WH_graph.add_node(node_name, coords = p, index=(i,j), node_type = "S" , conn=conn)
            self.WH_shelf_node_list.append(node_name)
            self.WH_grid[i][j] = node_name
    
    def set_blocks(self, pos):
        """
        Args:
          pos: list of (x,y) of each block.
        """
        
        for p in pos:
            i,j = self.xy_to_ij(p[0], p[1])
            node_name = self.block_form(*p)
            self.WH_graph.add_node(node_name, coords = p, index=(i,j), node_type = "B" , conn='N')
            self.WH_block_node_list.append(node_name)
            self.WH_grid[i][j] = node_name
    
    def fill_aisles(self):
        """
        Args: 
          None
        Note:
          Fill the rest of the grid with asile nodes.
        """
        
        for i,r in enumerate(self.WH_grid):
            for j,c in enumerate(r):
                if "AISLE_" in c:
                    x,y  = self.ij_to_xy(i,j)
                    self.WH_graph.add_node(c, coords = (x,y), index=(i,j), node_type = "A" , conn='A')
                    self.WH_aisle_node_list.append(c)
                    self.WH_grid[i][j] = c
                    
    def build_layout(self):
        """
        Args:
          None
        Note:
          Build Warehouse graph based on the doors, shelves, blocks.
        """
        
        self.fill_aisles()
        self.link_row_wise()
        self.link_column_wise()
        
#         print('Layout')
#         print(self.WH_grid)
#         print('\n\nConnections')
#         print(self.WH_graph.edges)
    
    def get_layout_for_render(self):
        coords=nx.get_node_attributes(self.WH_graph,'coords')
        conn = nx.get_node_attributes(self.WH_graph,'conn')
        retDict = {
            'X_RANGE' : (0, self.WH_width-1),
            'Y_RANGE' : (0, self.WH_height-1),
            'DOORS'   : [(*coords[n], conn[n]) for n in self.WH_door_node_list],
            'SHELVES' : [(*coords[n], conn[n]) for n in self.WH_shelf_node_list],
            'BLOCKS'  : [coords[n] for n in self.WH_block_node_list]
        }
        
        return retDict
    
    def set_zone_counter(self, itemManager):
        
        zone_counters = {}

        for z in self.zones:

            z_cnt = collections.Counter()
            for shelf in self.zones[z]['SHELF']:

                z_cnt = z_cnt + collections.Counter(itemManager.shelves[shelf])

            zone_counters[z] = z_cnt

        self.zone_counter = zone_counters
    
    def tmp_set_zone(self, zone_name, shelf_node_list_in_zone, aisle_node_list_in_zone):
        
        cx = 0
        cy = 0
        
        vmin = 100000
        vmax = -1
        
        hmin = 100000
        hmax = -1
        
        coords=nx.get_node_attributes(self.WH_graph,'coords')
        count = 0
       # print(shelf_node_list_in_zone)
        for sn in shelf_node_list_in_zone:
            #print(coords[sn])
            cx += coords[sn][0]
            cy += coords[sn][1]
            count += 1
        #print(aisle_node_list_in_zone)
        for an in aisle_node_list_in_zone:
            #print(coords[an])
            
            ax, ay = coords[an][0], coords[an][1]
            
            cx += ax
            cy += ay
            
            if vmin > ay:
                vmin = ay
            if vmax < ay:
                vmax = ay
            if hmin > ax:
                hmin = ax
            if hmax < ax:
                hmax = ax
            
            vgap = vmax-vmin
            hgap = hmax-hmin
            
            zone_type = 'V'
            
            if hgap > vgap:
                zone_type = 'H'
            
            count += 1
            
        cx /= count
        cy /= count
        
        self.zones[zone_name] = {'SHELF':shelf_node_list_in_zone, 'AISLE':aisle_node_list_in_zone, 'CENTER':(cx,cy), 'ZONE_TYPE':zone_type}
        
        if 'D' in zone_name:
            for a in aisle_node_list_in_zone:
                self.zone_door_map[a] = zone_name
        
        
    def tmp_abstract_graph(self):
        
        self.WH_abstract_graph = nx.Graph()
        
        
        ref = [
            ['Z{}_4'.format(i) for i in range(1,11) ],
            ['Z{}_3'.format(i) for i in range(1,11) ],
            ['Z{}_2'.format(i) for i in range(1,11) ],
            ['Z{}_1'.format(i) for i in range(1,11) ],
            ['D{}'.format(i) for i in range(1,11)]
        ]
        
        for a,b,c,d,e in zip(*ref):
            self.WH_abstract_graph.add_edge(a,  b, weight=11)
            self.WH_abstract_graph.add_edge(b,  c, weight=12)
            self.WH_abstract_graph.add_edge(c,  d, weight=11)
            self.WH_abstract_graph.add_edge(d, e, weight=7)

        ref2 = [15 + 3*i for i in range(9)]
        ref3 = [10 + 3*i for i in range(9)]
        ref4 = [3 + 3*i for i in range(9)]
        
        ref_zx_1 = [1+i*3 for i in range(10)]
        ref_dx = [1+i*3 for i in range(10)]
        
        for i,zx in enumerate(ref_zx_1):
            for j, dx in enumerate(ref_dx):
                self.WH_abstract_graph.add_edge(ref[3][i], ref[4][j], weight= abs(zx-dx)+7)
        
        for i in range(9):
            for j in range(i, 10):
                
                dx1 = ref_dx[i]
                dx2 = ref_dx[j]
        
        
        
                self.WH_abstract_graph.add_edge(ref[4][i], ref[4][j], weight= abs(dx1-dx2) + 2)
        for i in range(10):
            
            fromz4 = ref[0][i]
            fromz3 = ref[1][i]
            fromz2 = ref[2][i]
            fromz1 = ref[3][i]
            fromd = ref[4][i]
            
            self.zones[fromz4]['TIE_APPROACH'] = 'UD'
            self.zones[fromz3]['TIE_APPROACH'] = 'DU'
            self.zones[fromz2]['TIE_APPROACH'] = 'UD'
            self.zones[fromz1]['TIE_APPROACH'] = 'DU'
            self.zones[fromd]['TIE_APPROACH'] = 'UD'
            
            tozs4 = ref[0][i+1:]
            tozs3 = ref[1][i+1:]
            tozs2 = ref[2][i+1:]
            tozs1 = ref[3][i+1:]
            for j in range(len(tozs4)):
                
                self.WH_abstract_graph.add_edge(fromz4, tozs4[j], weight=ref2[j])
                
                self.WH_abstract_graph.add_edge(fromz3, tozs3[j], weight=ref2[j])
                self.WH_abstract_graph.add_edge(fromz2, tozs3[j], weight=ref2[j])
                self.WH_abstract_graph.add_edge(fromz2, tozs2[j], weight=ref2[j])
                self.WH_abstract_graph.add_edge(fromz1, tozs1[j], weight=ref2[j])
                    


def gen_test_wh_layout():
    wh = Warehouse()

    wh.set_grid_layout(30, 49)

    wh.set_doors([(1, 0), (4, 0), (7, 0), (10, 0), (13, 0), (16, 0), (19, 0), (22, 0), (25, 0), (28, 0)])

    wh.set_shelves([(0, i) for i in range(2, 47)], 'R')
    wh.set_shelves([(29, i) for i in range(2, 47)], 'L')

    for x in [2 + 3 * j for j in range(9)]:
        wh.set_shelves([(x, i) for i in range(2, 24)], 'L')
        wh.set_shelves([(x, i) for i in range(25, 47)], 'L')

        wh.set_shelves([(x + 1, i) for i in range(2, 47)], 'R')
        wh.set_shelves([(x + 1, i) for i in range(25, 47)], 'R')

    wh.build_layout()

    return wh

def gen_test_zone(wh_, im):

    wh = deepcopy(wh_)

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
    wh.tmp_set_zone('Z1_4', ['SHELF_(0,{})'.format(i) for i in sc4] + ['SHELF_(2,{})'.format(i) for i in sc4],
                    ['AISLE_(1,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z1_3', ['SHELF_(0,{})'.format(i) for i in sc3] + ['SHELF_(2,{})'.format(i) for i in sc3],
                    ['AISLE_(1,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z1_2', ['SHELF_(0,{})'.format(i) for i in sc2] + ['SHELF_(2,{})'.format(i) for i in sc2] + [
        'SHELF_(0,24)'], ['AISLE_(1,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z1_1', ['SHELF_(0,{})'.format(i) for i in sc1] + ['SHELF_(2,{})'.format(i) for i in sc1],
                    ['AISLE_(1,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z2_4', ['SHELF_(3,{})'.format(i) for i in sc4] + ['SHELF_(5,{})'.format(i) for i in sc4],
                    ['AISLE_(4,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z2_3', ['SHELF_(3,{})'.format(i) for i in sc3] + ['SHELF_(5,{})'.format(i) for i in sc3],
                    ['AISLE_(4,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z2_2', ['SHELF_(3,{})'.format(i) for i in sc2] + ['SHELF_(5,{})'.format(i) for i in sc2],
                    ['AISLE_(4,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z2_1', ['SHELF_(3,{})'.format(i) for i in sc1] + ['SHELF_(5,{})'.format(i) for i in sc1],
                    ['AISLE_(4,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z3_4', ['SHELF_(6,{})'.format(i) for i in sc4] + ['SHELF_(8,{})'.format(i) for i in sc4],
                    ['AISLE_(7,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z3_3', ['SHELF_(6,{})'.format(i) for i in sc3] + ['SHELF_(8,{})'.format(i) for i in sc3],
                    ['AISLE_(7,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z3_2', ['SHELF_(6,{})'.format(i) for i in sc2] + ['SHELF_(8,{})'.format(i) for i in sc2],
                    ['AISLE_(7,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z3_1', ['SHELF_(6,{})'.format(i) for i in sc1] + ['SHELF_(8,{})'.format(i) for i in sc1],
                    ['AISLE_(7,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z4_4', ['SHELF_(9,{})'.format(i) for i in sc4] + ['SHELF_(11,{})'.format(i) for i in sc4],
                    ['AISLE_(10,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z4_3', ['SHELF_(9,{})'.format(i) for i in sc3] + ['SHELF_(11,{})'.format(i) for i in sc3],
                    ['AISLE_(10,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z4_2', ['SHELF_(9,{})'.format(i) for i in sc2] + ['SHELF_(11,{})'.format(i) for i in sc2],
                    ['AISLE_(10,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z4_1', ['SHELF_(9,{})'.format(i) for i in sc1] + ['SHELF_(11,{})'.format(i) for i in sc1],
                    ['AISLE_(10,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z5_4', ['SHELF_(12,{})'.format(i) for i in sc4] + ['SHELF_(14,{})'.format(i) for i in sc4],
                    ['AISLE_(13,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z5_3', ['SHELF_(12,{})'.format(i) for i in sc3] + ['SHELF_(14,{})'.format(i) for i in sc3],
                    ['AISLE_(13,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z5_2', ['SHELF_(12,{})'.format(i) for i in sc2] + ['SHELF_(14,{})'.format(i) for i in sc2],
                    ['AISLE_(13,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z5_1', ['SHELF_(12,{})'.format(i) for i in sc1] + ['SHELF_(14,{})'.format(i) for i in sc1],
                    ['AISLE_(13,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z6_4', ['SHELF_(15,{})'.format(i) for i in sc4] + ['SHELF_(17,{})'.format(i) for i in sc4],
                    ['AISLE_(16,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z6_3', ['SHELF_(15,{})'.format(i) for i in sc3] + ['SHELF_(17,{})'.format(i) for i in sc3],
                    ['AISLE_(16,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z6_2', ['SHELF_(15,{})'.format(i) for i in sc2] + ['SHELF_(17,{})'.format(i) for i in sc2],
                    ['AISLE_(16,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z6_1', ['SHELF_(15,{})'.format(i) for i in sc1] + ['SHELF_(17,{})'.format(i) for i in sc1],
                    ['AISLE_(16,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z7_4', ['SHELF_(18,{})'.format(i) for i in sc4] + ['SHELF_(20,{})'.format(i) for i in sc4],
                    ['AISLE_(19,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z7_3', ['SHELF_(18,{})'.format(i) for i in sc3] + ['SHELF_(20,{})'.format(i) for i in sc3],
                    ['AISLE_(19,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z7_2', ['SHELF_(18,{})'.format(i) for i in sc2] + ['SHELF_(20,{})'.format(i) for i in sc2],
                    ['AISLE_(19,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z7_1', ['SHELF_(18,{})'.format(i) for i in sc1] + ['SHELF_(20,{})'.format(i) for i in sc1],
                    ['AISLE_(19,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z8_4', ['SHELF_(21,{})'.format(i) for i in sc4] + ['SHELF_(23,{})'.format(i) for i in sc4],
                    ['AISLE_(22,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z8_3', ['SHELF_(21,{})'.format(i) for i in sc3] + ['SHELF_(23,{})'.format(i) for i in sc3],
                    ['AISLE_(22,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z8_2', ['SHELF_(21,{})'.format(i) for i in sc2] + ['SHELF_(23,{})'.format(i) for i in sc2],
                    ['AISLE_(22,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z8_1', ['SHELF_(21,{})'.format(i) for i in sc1] + ['SHELF_(23,{})'.format(i) for i in sc1],
                    ['AISLE_(22,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z9_4', ['SHELF_(24,{})'.format(i) for i in sc4] + ['SHELF_(26,{})'.format(i) for i in sc4],
                    ['AISLE_(25,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z9_3', ['SHELF_(24,{})'.format(i) for i in sc3] + ['SHELF_(26,{})'.format(i) for i in sc3],
                    ['AISLE_(25,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z9_2', ['SHELF_(24,{})'.format(i) for i in sc2] + ['SHELF_(26,{})'.format(i) for i in sc2],
                    ['AISLE_(25,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z9_1', ['SHELF_(24,{})'.format(i) for i in sc1] + ['SHELF_(26,{})'.format(i) for i in sc1],
                    ['AISLE_(25,{})'.format(i) for i in sc1])

    wh.tmp_set_zone('Z10_4', ['SHELF_(27,{})'.format(i) for i in sc4] + ['SHELF_(29,{})'.format(i) for i in sc4],
                    ['AISLE_(28,{})'.format(i) for i in sc4])
    wh.tmp_set_zone('Z10_3', ['SHELF_(27,{})'.format(i) for i in sc3] + ['SHELF_(29,{})'.format(i) for i in sc3],
                    ['AISLE_(28,{})'.format(i) for i in sc3])
    wh.tmp_set_zone('Z10_2', ['SHELF_(27,{})'.format(i) for i in sc2] + ['SHELF_(29,{})'.format(i) for i in sc2],
                    ['AISLE_(28,{})'.format(i) for i in sc2])
    wh.tmp_set_zone('Z10_1', ['SHELF_(27,{})'.format(i) for i in sc1] + ['SHELF_(29,{})'.format(i) for i in sc1] + [
        'SHELF_(29,24)'], ['AISLE_(28,{})'.format(i) for i in sc1])
    wh.tmp_abstract_graph()

    wh.set_zone_counter(im)

    return wh
        
if __name__ == "__main__":
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


        