
class Quadtree(object):
    """     
    "The point quadtree is an adaptation of a binary tree used to 
    represent two dimensional point data." This data structure exhibits 
    O(log(n)) search times for given point data, making it very useful for
    searching on a 2D grid.
    """
    
    __slots__ = ('min_x', 'max_x', 'min_y', 'max_y', 'elements',
                 'bucket_size', 'is_node', 'nw', 'ne', 'sw', 'se')

    def __init__(self, min_x, max_x, min_y, max_y, bucket_size=40):
        """
        Creates a quadtree with given boundaries and bucket limit.
        
        Arguments:
        min_x, max_x, min_y, max_y -- boundaries

        Keyword Arguments:
        bucket_size -- max number of elements to be stored in leaves
                        (40 is a good number for memory and performance)
        """
        self.bucket_size = int(bucket_size)
        self.min_x = float(min_x)
        self.max_x = float(max_x)
        self.min_y = float(min_y)
        self.max_y = float(max_y)
        self.elements = {}
        self.is_node = False

    def insert(self, point, data=None):
        point = tuple(point)
        if not self.in_bounds(point):
            return False
        pointer = self
        while True:
            if pointer.is_node:
                pointer = pointer.select_child(point)    # descend into the tree
            elif len(pointer.elements) >= pointer.bucket_size:
                pointer.branch()
                pointer = pointer.select_child(point)
            else:
                pointer.elements[point] = data  # add the element
                return True
        assert False, 'Should never get here!'
    
    def branch(self):
        self.convert_to_node()
        for point, data in self.elements.iteritems():
            self.select_child(point).elements[point] = data
        del self.elements

    def convert_to_node(self):
        self.is_node = True
        dx = self.max_x - self.min_x
        dy = self.max_y - self.min_y
        mid_x = self.min_x + dx / 2
        mid_y = self.min_y + dy / 2
        buckets = self.bucket_size
        self.nw = Quadtree(self.min_x, mid_x, mid_y, self.max_y, buckets)
        self.ne = Quadtree(mid_x, self.max_x, mid_y, self.max_y, buckets)
        self.se = Quadtree(mid_x, self.max_x, self.min_y, mid_y, buckets)
        self.sw = Quadtree(self.min_x, mid_x, self.min_y, mid_y, buckets)
    
    def query_range(self, min_x, max_x, min_y, max_y):
        result = {}
        untried = [self]
        while untried:
            pointer = untried.pop()
            if (pointer.is_node and 
                    pointer.rect_intersect(min_x, max_x, min_y, max_y)):
                untried.extend(pointer.get_children())
            else:
                elements = pointer.elements
                for value in elements:
                    x, y = value
                    if not (min_x > x or x > max_x or min_y > y or y > max_y):
                        result[value] = elements[value]
        return result
    
    def select_child(self, point):
        dx = self.max_x - self.min_x
        dy = self.max_y - self.min_y
        x, y = point
        west = self.min_x <= x and x <= self.min_x + dx / 2
        north = self.min_y + dy / 2 <= y and y <= self.max_y
        if west:
            return self.nw if north else self.sw
        else:
            return self.ne if north else self.se

    def rect_intersect(self, min_x, max_x, min_y, max_y):
        """Returns whether this rectangle intersects with another."""
        return not (self.min_x > max_x or self.max_x < min_x or
                    self.min_y > max_y or self.max_y < min_y)
        
    def in_bounds(self, point):
        x, y = point
        return ((self.min_x <= x and x <= self.max_x) and 
                (self.min_y <= y and y <= self.max_y))

    def get_children(self):
        return self.nw, self.ne, self.sw, self.se


# class MultiQuadtree(Quadtree):

#     def __init__(self, min_x, max_x, min_y, max_y, bucket_size=40):
#         Quadtree.__init__(self, min_x, max_x, min_y, max_y, bucket_size=40)


def bounding_box(point_list):
    """ Given a list of points, return a bounding box containing them all. """
    max_x, max_y = float('-inf'), float('-inf')
    min_x, min_y = float('inf'), float('inf')
    for x_pnt, y_pnt in point_list:
        if x_pnt > max_x:
            max_x = x_pnt
        elif x_pnt < min_x:
            min_x = x_pnt
        if y_pnt > max_y:
            max_y = y_pnt
        elif y_pnt < min_y:
            min_y = y_pnt
    return min_x, max_x, min_y, max_y

if __name__ == '__main__':
    import cProfile, random, time
    max_rng = 10000
    size = 10000
    testarr = [(random.randint(0, max_rng), random.randint(0, max_rng)) 
                for _ in xrange(size)]
    qtree = Quadtree(0, max_rng, 0, max_rng)
    def main():
        for integer in testarr:
            qtree.insert(integer)        

    start = time.time()
    main()
    print len(qtree.query_range(0, 10000, 0, 10000))
    print time.time() - start
    #cProfile.run('main()', sort=1)