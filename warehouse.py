import networkx as nx


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
                if conn[left] in ('A', 'R') and conn[right] in ('A','L') and not ('SHELF' in left and 'SHELF' in right):                
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
                if (conn[up] in ('A', 'D') and conn[down] in ('A','U')) and not ('SHELF' in up and 'SHELF' in down) :           
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
          conn: direction of shelf face. One of {'A'(ll), 'L'(eft), 'R'(ight), 'U'(p), 'D'(own), 'N'(one)}.
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
        retDict = {
            'X_RANGE' : (0, self.WH_width-1),
            'Y_RANGE' : (0, self.WH_height-1),
            'DOORS'   : [coords[d] for d in self.WH_door_node_list],
            'SHELVES' : [coords[d] for d in self.WH_shelf_node_list],
            'BLOCKS'  : [coords[d] for d in self.WH_block_node_list]
        }
        
        return retDict

        