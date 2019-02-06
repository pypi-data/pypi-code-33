'''
Created on Nov 3, 2014

@author: thocu
'''
import itertools
from VirtualMicrobes.my_tools.utility import CircularList, Coord
import numpy as np
import collections
import copy


class GridError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PositionOutsideGridError(GridError):
    def __init__(self, x,y):
        self.value = (x,y)
        
    def __str__(self):
        return repr(self.value)

class Neighborhood(object):
    '''
    Neighborhood as grid indices (x,y coord tuples) relative to a focal gridpoint. 
    '''
    
    def __init__(self, neighbors):
        '''
        Constructs neighborhood object
        
        :param neighbors: either a scalar, determining the 'radius of x and y
        relative to focal gp or a list of (x,y) tuples of neighbor coordinates
        relative to focal gp
        '''
        if isinstance(neighbors, list):
            self.construct_neighbors(neighbors)
        elif isinstance(neighbors, int):
            self.construct_moore_n(neighbors)
        elif isinstance(neighbors, str):
            self.construct_named_neighborhood(neighbors)
        else:
            raise Exception('Could not construct neighborhood from argument', neighbors)
    
    def construct_neighbors(self, neighbors):
        self.nei_rel_coords = [ Coord(x,y) for (x,y) in neighbors ]
    
    def construct_moore_n(self, perim=1, exclude_self=True):
        self.nei_rel_coords = [ Coord(x,y) for x in range(-perim, perim+1) 
                             for y in range(-perim, perim+1) 
                             if ( not (exclude_self and x==0 and y==0) ) ]
        
    def construct_neumann_n(self, manhatten=1, exclude_self=True):
        self.nei_rel_coords = [ Coord(x,y) for x in range(-manhatten, manhatten+1) 
                             for y in range(-manhatten, manhatten+1) 
                             if ( not (exclude_self and x==0 and y==0) ) and abs(x)+abs(y) <=manhatten ]
        
    def construct_named_neighborhood(self, name):
        if name in ['neumann', 'neumann4']:
            self.construct_neumann_n(1)
        elif name in ['moore', 'moore8']:
            self.construct_moore_n(1)
        elif name == 'moore9':
            self.construct_moore_n(1, exclude_self=False)
        elif name == 'neumann5':
            self.construct_neumann_n(1, exclude_self=False)
        elif name == 'neumann12':
            self.construct_neumann_n(2)
        elif name == 'moore24':
            self.construct_moore_n(2)
        elif name == 'neumann13':
            self.construct_neumann_n(2, exclude_self=False)
        elif name == 'moore25':
            self.construct_moore_n(2, exclude_self=False)
        else:
            raise Exception('no matching neighborhood found to construct', name)
        
    def get_rel_coords(self, area=None):
        """
        Return a list of neighborhood coordinates that lie in an area of the compass
        relative to (0,0)  
        
        Parameters
        ----------
        area : {'north', 'south', 'east', 'west'}
            The named area (or 'hemisphere') in grid space relative to the origin (0,0).
        
        Notes
        -----
        Compass directions translate to relative coordinates as shown below:
        _________________________________________
        |                                        |
        |                                        |
        |      N            (0, 1)               |
        |    W   E    (-1,0)      (1,0)          |
        |      S            (0,-1)               |
        |                                        |
        |________________________________________|
        
        Returns
        -------
        list of :class:`my_tools.utility.Coord`s
            The coordinates that lie within the named area.
        """
        coords = []
        if area is not None:
            if area == 'north':
                coords = [ coord for coord in self.nei_rel_coords if coord.y > 0 ]
            elif area == 'south':
                coords = [ coord for coord in self.nei_rel_coords if coord.y < 0 ]
            elif area == 'east':
                coords = [ coord for coord in self.nei_rel_coords if coord.x > 0 ]
            elif area == 'west':
                coords = [ coord for coord in self.nei_rel_coords if coord.x < 0 ]
            else:
                raise Exception('{0} is not a area'.format(area))
        else:
            coords = self.nei_rel_coords
        return coords
    
    def has_coord(self, rel_coord):
        """
        Check that relative coordinate is part of this neighborhood.
        
        Parameters
        ----------
        rel_coord : :class:`my_tools.utility.Coord`
        """
        for nei_coord in self.nei_rel_coords:
            if nei_coord == rel_coord:
                return True
        return False
    
    def remove_coord(self, remove_coord):
        '''
        Remove a relative coordinate from the neighborhood.
        
        Parameters
        ----------
        remove_coord : :class:`my_tools.utility.Coord`
        '''
        found = False
        for coord in self.nei_rel_coords[:]:
            if coord == remove_coord:
                self.nei_rel_coords.remove(coord)
                found = True
        if not found:
            raise Exception('coord {0} not found. It cannot be removed'.format(remove_coord))
    
    def remove_direction(self, direction):
        '''
        Remove coordinates lying to the given direction on the grid, where the
        main compass points are translated into coordinates as follows:
        
        The main compass points are translated into coordinates as follows:
          N            (0, 1)
        W   E    (-1,0)      (1,0)
          S            (0,-1) 
        e.g. when direction is 'north', all relative coordinates that lie northerly of 
        the (0,0) will be removed.
        
        Parameters
        ----------
        direction : {'north', 'south', 'east', 'west'}, optional
            Selects those coordinates in the neighborhood that lie in a
            particular direction (default is None, which implies returninng all
            coordinates.
        '''
        if direction == 'north':
            self.nei_rel_coords = [ coord for coord in self.nei_rel_coords if coord.y <= 0 ]
        elif direction == 'south':
            self.nei_rel_coords = [ coord for coord in self.nei_rel_coords if coord.y >= 0 ]
        elif direction == 'east':
            self.nei_rel_coords = [ coord for coord in self.nei_rel_coords if coord.x <= 0 ]
        elif direction == 'west':
            self.nei_rel_coords = [ coord for coord in self.nei_rel_coords if coord.x >= 0 ]
        else:
            raise Exception('{0} is not a direction'.format(direction))
        
    def __len__(self):
        return len(self.nei_rel_coords)
    
    def __str__(self):
        return ', '.join(["("+ str(coord.x)+ "," + str(coord.y) + ")"  
                         for coord in self.nei_rel_coords])

class GridPoint(object):
    
    def __init__(self, (x,y) , val, neighborhood_dict, grid):
        self.coord = Coord(x,y)
        self.content = val
        self.grid = grid
        self.neighborhoods = neighborhood_dict
        self.updated = True
    
    @property
    def updated(self):
        return self._updated
    
    @updated.setter
    def updated(self, val):
        if not isinstance(val, bool):
            raise ValueError('updated should be of type bool, not {}'.format(type(val)))
        self._updated = val
        
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, val):
        self._content = val
        
    @property
    def coord(self):
        return self._coord
    
    @coord.setter
    def coord(self, new_coord):
        self._coord = new_coord
        
    def nei_grid_coords(self, neighborhood_name, area=None):
        return [ Coord(self.coord.x + nei_x, self.coord.y + nei_y) 
            for (nei_x,nei_y) in self[neighborhood_name].get_rel_coords(area) ]

    def nei_rel_to_grid_coords(self, neighborhood_name, area=None):
        """
        List of (relative-coordinate, grid-coordinate) tuples of the named neighborhood.
        
        Parameters
        ----------
        
        neighborhood_name : str
            Name of the neighborhood
        area :  {'north', 'south', 'east', 'west'}, optional
            Select only neighbors lying in a specific area
            
        Returns
        -------
        list of (:class:`my_tools.utility.Coord`, :class:`my_tools.utility.Coord`) tuples
        """
        return [ (nei_coord, Coord(self.coord.x + nei_coord.x, self.coord.y + nei_coord.y) ) 
            for nei_coord in self[neighborhood_name].get_rel_coords(area) ]
        
    def nei_rel_coord_to_gp(self, neighborhood_name, area=None):
        """
        List of (relative-coordinate,grid-point) tuples of the named neighborhood.
        
        Parameters
        ----------
        neighborhood_name : str
            Name of the neighborhood
        area :  {'north', 'south', 'east', 'west'}, optional
            Select only neighbors lying in a specific area.
            
        Returns
        -------
        list of (:class:`my_tools.utility.Coord`, :class:`GridPoint`) tuples
        """
        return [ (nei_coord, self.get_neighbor_at(nei_coord, neighborhood_name) ) 
                  for nei_coord in self[neighborhood_name].get_rel_coords(area) ]
        
    def get_neighbor_at(self, rel_coord, neighborhood_name):
        """
        Get neighboring grid point at a relative coordinate.
        
        Parameters
        ----------
        rel_coord : :class:`my_tools.utility.Coord`
            coordinate relative to self
        neighborhood_name : str
            Name of the neighborhood.
            
        Returns
        -------
        :class:`GridPoint`
            The neighboring grid point. 
        """
        if not self[neighborhood_name].has_coord(rel_coord):
            raise Exception('coordinate {} not in neighborhood {}'.format(rel_coord, neighborhood_name))
        return self.grid.get_gp( self.coord.x + rel_coord.x, self.coord.y + rel_coord.y)
        
    def remove_neighbor_at(self, rel_coord, neighborhood_name):
        """
        Remove a coordinate from a named neighborhood.
        
        After removing the relative coordinate `rel_coord`, the corresponding
        grid point is no longer considered a neighbor of `self` when applying
        neighborhood functions.
        
        Parameters
        ----------
        rel_coord : :class:`my_tools.utility.Coord`
            Coordinate relative to self.
        neighborhood_name : str
            Name of the neighborhood.
        """
        self[neighborhood_name].remove_coord(rel_coord)
        
    def neighbors(self, neighborhood_name, area=None):
        """
        Return list of grid point content values of neighbors in named neighborhood.
        
        Parameters
        ----------
        neighborhood_name : str
            Name of the neighborhood.
        area :  {'north', 'south', 'east', 'west'}, optional
            Select only neighbors lying in a specific area.
            
        Returns
        -------
        """
        return self.grid._get_neighbors(self, neighborhood_name, area)
    
    def neighbor_gps(self, neighborhood_name, area=None):
        '''
        Return list of grid points in a named neighborhood.
        
        Parameters
        ----------
        neighborhood_name : str
            Name of the neighborhood.
        area :  {'north', 'south', 'east', 'west'}, optional
            Select only neighbors lying in a specific area.
        """
        '''
        return self.grid._get_neighboring_gps(self, neighborhood_name, area)
    
    def random_neighbor(self, neighborhood_name, rand_gen, area=None):
        """
        Get random neighbor from a named neighborhood.
        
        Parameters
        ----------
        neighborhood_name : str
            Name of the neighborhood.
        rand_gen : random generator
            Random generator for neighbor drawing.
        area :  {'north', 'south', 'east', 'west'}, optional
            Select only neighbors lying in a specific area.
        """
        nei_gps = self.neighbor_gps(neighborhood_name, area)
        if not nei_gps:
            return
        return rand_gen.choice(nei_gps)
            
        
        
    
    @property
    def pos(self):
        return (self.coord.x , self.coord.y)

    def __getitem__(self,key):
        try:
            nei = self.neighborhoods[key]
        except KeyError:
            raise KeyError('key not found in dict', key, self.neighborhoods)
        return nei
    
    def __str__(self):
        return "("+ str(self.coord.x)+ "," + str(self.coord.y) + ")" # + str(self.content)
            

def mirror_rel_coord(coord):
    return Coord(x=-coord.x, y=-coord.y)

class Grid(object):
    '''
    Grid will by default be wrapped, because the Neighborhood will index 
    '''
    
    def __init__(self, rows, cols, neighborhood_dict=None, nei_wrapped_ew=None, nei_wrapped_ns=None):
        self.rows = rows
        self.cols = cols
        if neighborhood_dict is None:
            self.neighborhood_dict = {'competition': Neighborhood('moore9'), 
                                      'diffusion': Neighborhood('neumann'),
                                      'hgt': Neighborhood('neumann13')
                                      }
        else:
            self.neighborhood_dict = neighborhood_dict
        self.init_grid(self.rows, self.cols, self.neighborhood_dict)
        if nei_wrapped_ew is None:
            nei_wrapped_ew = self.neighborhood_dict.keys()
        self.nei_wrapped_ew = nei_wrapped_ew
        if nei_wrapped_ns is None:
            nei_wrapped_ns = self.neighborhood_dict.keys()
        self.nei_wrapped_ns = nei_wrapped_ns
        for nei in self.neighborhood_dict.keys():
            if nei not in self.nei_wrapped_ew:
                self.unwrap_ew(nei)
            if nei not in self.nei_wrapped_ns:
                self.unwrap_ns(nei)
        self.named_direction_map = {'N':Coord(0,1), 'NE':Coord(1,1), 'E':Coord(1,0) , 'SE':Coord(1,-1), 
                                    'S':Coord(0,-1) , 'SW':Coord(-1,-1), 'W':Coord(-1,0), 'NW':Coord(-1,1),
                                    'C':Coord(0,0)}
        
    def init_grid(self, rows, cols, neighborhood_dict, wrap_ew=None, wrap_ns=None):
        self.grid = CircularList([ CircularList([ GridPoint((x,y), None, copy.deepcopy(neighborhood_dict), self) 
                       for x in range(cols) ]) 
                     for y in range(rows)])
    
    def unwrap_ew(self, neighborhood_name):
        """
        Unwraps a grid neighborhood at its eastern and western borders.
        
        Iterate over all grid points and detect when a grid point has neighbors that wrap
        over the east or west borders. Then remove the coordinate from the neighborhood. 
        
        Parameters
        ----------
        neighborhood_name : str
            The name of the neighborhood to unwrap
            
        Notes
        -----
        For a wrapped neighbor it is true that the difference between the focal
        gp coordinate and this neighbors (normalized) grid-coordinate is not
        equal to the its relative-coordinate (to focal gp).
        
        See Also
        --------
        :func:`unwrap_ns`
        :func:`normalize_coord`
        """
        for gp in self.gp_iter:
            x = self.normalize_coord(gp.coord).x
            for nei_rel_coord, nei_grid_coord in gp.nei_rel_to_grid_coords(neighborhood_name):
                if  self.normalize_coord(nei_grid_coord).x - x != nei_rel_coord.x: # test if this neighbor is wrapped
                    gp.remove_neighbor_at(nei_rel_coord, neighborhood_name) 
                    
    def unwrap_ns(self, neighborhood_name):
        """
        Unwraps a grid neighborhood at its northern and southern borders.
        
        Iterate over all grid points and detect when a grid point has neighbors that wrap
        over the north or south borders. Then remove the coordinate from the neighborhood.
        
        Parameters
        ----------
        neighborhood_name : str
            The name of the neighborhood to unwrap
            
        Notes
        -----
        For a wrapped neighbor it is true that the difference between the focal
        gp coordinate and this neighbors (normalized) grid-coordinate is not
        equal to the its relative-coordinate (to focal gp).
        
        See Also
        --------
        :func:`unwrap_ew`
        :func:`normalize_coord`
        """
        for gp in self.gp_iter:
            y = self.normalize_coord(gp.coord).y
            for nei_rel_coord, nei_grid_coord in gp.nei_rel_to_grid_coords(neighborhood_name):
                if  self.normalize_coord(nei_grid_coord).y - y != nei_rel_coord.y: # test if this neighbor is wrapped
                    gp.remove_neighbor_at(nei_rel_coord, neighborhood_name)
                        
    def normalize_coord(self, coord):
        """
        Transform coordinate `coord` to an absolute grid coordinate with non-
        wrapped index.
        
        Applies modulo :attr:`cols` and :attr:`rows` on the coordinates x
        and y value, respectively, to obtain a normalized coordinate.   
        
        Parameters
        ----------
        coord : :class:`my_tools.utility.Coord`
            a coordinate on the grid that may be in wrapped index representation
            
        Returns
        -------
        :class:`my_tools.utility.Coord`
        """
        return Coord( x= coord.x % self.cols , y= coord.y % self.rows )
    
    def un_neighbor(self, gp, nei_rel_coord, neighborhood):
        nei_gp = gp.get_neighbor_at(nei_rel_coord, neighborhood)
        gp.remove_neighbor_at(nei_rel_coord, neighborhood)
        nei_gp.remove_neighbor_at(mirror_rel_coord(nei_rel_coord), neighborhood)
            
    def disconnect_direction(self, gp, area, neighborhood):
        '''
        For all neighboring grid points lieing in a particular `direction` in a
        named `neighborhood` of a grid point `gp`, remove the `gp` coordinate
        from their neighborhoods.
        
        e.g. if area is 'south' , the southern neighbors of gp will remove gp's 
        relative coordinate from their neighborhood
        
        Parameters
        ----------
         
        gp : :class:`GridPoint` 
            Grid point that will get unwrapped.
            
        direction : {'north', 'south', 'east', 'west'}, optional
            The direction relative to the `gp`. 
            
        neighborhood : str
            named neighborhood for which the unwrapping is done
        
        '''
        for nei_rel_coord in gp[neighborhood].get_rel_coords(area):
            self.un_neighbor(gp, nei_rel_coord, neighborhood)
            
    def make_barrier(self, start_coord, length, neighborhood_name, direction='lr' ):
        '''
        Create a barrier on the grid where interaction between adjacent grid points is blocked. 
        
        Create a barrier in the given neighborhood_name by unwrapping gps on opposite sides 
        of a line that is `length` long, starts at `start_gp` and extends along `direction`
        '''
        focal_gp = self.get_gp(*start_coord)
        if direction == 'lr':
            opposite, unwrap_area_forth, unwrap_back, proceed_direction = 'N', 'north', 'south', 'E'
        elif direction == 'tb':
            opposite, unwrap_area_forth, unwrap_back, proceed_direction = 'E', 'east', 'west', 'S'
        for _ in range(length):
            self.disconnect_direction(focal_gp, unwrap_area_forth, neighborhood_name)
            oposite_gp = self.get_nei_gp(focal_gp, opposite)
            self.disconnect_direction(oposite_gp, unwrap_back, neighborhood_name)
            focal_gp = self.get_nei_gp(focal_gp, proceed_direction)
    
    def grid_barriers(self, rand_gen, p_row=0., max_fraction_width=None, 
                      p_col=0., max_fraction_height=None, neighborhoods=None, ):
        '''
        Set up barriers in the grid 
        
        :param p_row:
        :param max_fraction_width:
        :param p_col:
        :param max_fraction_height:
        :param neighborhood:
        :param rand_gen:
        '''
        if neighborhoods is None:
            neighborhoods = self.neighborhood_dict.keys()
        max_width = int(max_fraction_width * self.cols) if max_fraction_width else None
        max_height = int(max_fraction_height * self.rows) if max_fraction_height else None
        for r in range(self.rows):
            if rand_gen.uniform(0,1.) < p_row:
                c = rand_gen.randint(0, self.cols)
                width = rand_gen.randint(0, max_width) if max_width else self.cols 
                for neighborhood in neighborhoods:
                    self.make_barrier(Coord(x=c, y=r), width, neighborhood, 'lr')
        for c in range(self.cols):
            if rand_gen.uniform(0,1.) < p_col:
                r = rand_gen.randint(0, self.rows)
                height = rand_gen.randint(0, max_height) if max_height else self.rows
                for neighborhood in neighborhoods:
                    self.make_barrier(Coord(x=c, y=r), height, neighborhood, 'tb')
                
    def columns_iter(self, cols, order = 'tb_lr'):            
        '''
        Iterate over gps in the selected columns 
        :param cols: selected columns 
        :param order: the order in which gps should be iterated
        '''
        return ( gp for gp in  self.gp_iter_in_order(order) if gp.coord.x in cols )
    
    def rows_iter(self, rows, order='lr_tb'):
        '''
        Iterate over gps in the selected rows
        '''
        return ( gp for gp in self.gp_iter_in_order(order) if gp.coord.y in rows)
    
    def mesh_iter(self, rows, cols, order='lr_tb'):
        '''
        iterate over gps in a mesh, defined by intersections of rows and cols
        '''
        return ( gp for gp in self.gp_iter_in_order(order) if gp.coord.y in rows and gp.coord.x in cols)
    
    @property
    def content_iter(self):
        return ( gp.content for gp in self.gp_iter)
    
    @property    
    def gp_iter(self):
        return itertools.chain(*self.grid)
    
    def _x_iter(self,reverse=False):
        it = (_ for _ in xrange(self.cols))
        if reverse:
            it = reverse(it)
        return it
    
    def _y_iter(self,reverse=False):
        it = (_ for _ in xrange(self.rows))
        if reverse:
            it = reverse(it)
        return it
        
    def gp_iter_in_order(self, order='lr_tb'):
        it = None
        if order == 'lr_tb':  # left to right, top to bottom
            #reverse_x, reverse_y, per_row = False, False, True
            return self.gp_iter
        elif order == 'lr_bt':
            reverse_x, reverse_y, per_row = False, True, True
        elif order == 'rl_tb':
            reverse_x, reverse_y, per_row = True, False, True
        elif order == 'rl_bt':
            reverse_x, reverse_y, per_row = True, True, True
        
        elif order == 'tb_lr':
            reverse_x, reverse_y, per_row = False, False, False
        elif order == 'tb_rl':
            reverse_x, reverse_y, per_row = True, False, False
        elif order == 'bt_lr':
            reverse_x, reverse_y, per_row = False, True, False
        elif order == 'bt_rl':
            reverse_x, reverse_y, per_row = True, True, False
        if per_row: 
            it = ( self.get_gp(x,y) for x in self._x_iter(reverse_x) for y in _y_iter(reverse_y) )
        else:
            it = ( self.get_gp(x,y) for y in self._y_iter(reverse_y) for x in self._x_iter(reverse_x))
        return it
        
    def update_gp(self,x,y,val):
        gp = self.get_gp(x, y)
        gp.content = val
    
    def set_gp(self,x,y, gp):
        self.grid[y][x] = gp
        
    def get_gp(self, x, y):
        return self.grid[y][x]
    
    def get_nei_gp(self, gp, direction_vect):
        if isinstance(direction_vect, str):
            direction_vect = self.named_direction_map[direction_vect]
        nei_x, nei_y = gp.coord.x + direction_vect.x, gp.coord.y + direction_vect.y
        return self.get_gp(nei_x, nei_y)
    
    def _get_neighbors(self, gp, neighborhood, direction=None):
        '''
        Get values in neighbors in 'neighborhood'
        :param neighborhood: key to neighborhood_dict in focal gp
        '''
        return [gp.content for gp in self._get_neighboring_gps(gp, neighborhood, direction)]
    
    def _get_neighboring_gps(self, gp, neighborhood_name, direction=None):
        neighbor_gps = []
        for nei_coord in gp.nei_grid_coords(neighborhood_name, direction):
            neighbor_gps.append(self.get_gp(nei_coord.x, nei_coord.y))
        return neighbor_gps   
    
    def fill_grid(self, vals, order='lr_tb'):
        if not isinstance(vals, collections.Iterable):
            vals = [ vals for _ in range(len(self))]
        for gp, l in zip(self.gp_iter_in_order(order),vals):
            gp.content = l
            
    def toggle_gps_updated(self, updated=False):
        for gp in self.gp_iter:
            gp.updated = updated
            
    def swap_content(self, gp1, gp2):
        val2 = gp2.content
        gp2.content = gp1.content
        gp1.content = val2
            
    def swap_gps(self,gp1, gp2):
        coord1 = gp1.coord
        coord2 = gp2.coord
        self.set_gp(coord1.x, coord1.y, gp2)
        self.set_gp(coord2.x, coord2.y, gp1)
        gp1.coord = coord2
        gp2.coord = coord2
        
    def swap_pos(self, pos1, pos2):
        gp1 = self.get_gp(*pos1)
        gp2 = self.get_gp(*pos2)
        self.swap_gps(gp1, gp2)
        
    def perfect_mix(self, rand_gen):
        gps = list(self.gp_iter)
        rand_gen.shuffle(gps)
        for i in range(len(gps)/2):
            self.swap_content(gps[i], gps[-i])
            
    @property
    def as_numpy_array(self):
        return np.array(self.grid)
            
    def __len__(self):
        return self.rows * self.cols
    
    def dummy(self):
        print 'dummy'
        
    def __getitem__(self,index):
        return self.grid[index]
    
    def __iter__(self):
        return self.gp_iter
    
    def __str__(self):
        nei_grids = []
        for nei in self.neighborhood_dict:
            nei_str = str(nei) + '\n'
            nei_str += '\n'.join( [ ' '.join([ str(gp) + ' ' + str(gp[nei])  for gp in row ]) for row in self.grid ] )
            nei_grids.append(nei_str)
        return '\n\n'.join(nei_grids )
    
if __name__ == "__main__":
    grid1 = Grid(5, 5, nei_wrapped_ew=['hgt'], nei_wrapped_ns=['hgt'] )
    print 'GRID1'
    for gp in grid1.gp_iter:
        print gp, 
        for nei_gp in gp.neighbor_gps('hgt'):
            print nei_gp,
        print
        
    grid2 = Grid(5, 5, nei_wrapped_ew=[], nei_wrapped_ns=[] )
    print
    print 'GRID2'
    for gp in grid2.gp_iter:
        print gp, 
        for nei_gp in gp.neighbor_gps('hgt'):
            print nei_gp,
        print
    
    
    print Coord(1,2) == Coord(1,2)
    print Coord(1,2) == Coord(1,3)
    print Coord(1,3) == Coord(1,3)
    
    import random
    random.uniform(-2.,-2.)
    #grid1.make_barrier(grid1[1][4], 4, 'hgt', 'tb')
    grid1.grid_barriers(p_row=1., p_col=0., neighborhoods=['hgt'], rand_gen=random)
    print
    print 'GRID2 with Barriers'
    for gp in grid1.gp_iter:
        print gp, 
        for nei_gp in gp.neighbor_gps('hgt'):
            print nei_gp,
        print
    
    
    print Coord(1,2) == Coord(1,2)
    print Coord(1,2) == Coord(1,3)
    print Coord(1,3) == Coord(1,3)
    
    
            
