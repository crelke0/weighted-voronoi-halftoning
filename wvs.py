import math
import random
from PIL import Image, ImageDraw

class Vector:
  # constructor for Vector
  # args {*} inputting nothing results in (0, 0), inputing "a" results in (a, a), inputting "a, b" results in (a, b)
  def __init__(self, *args):
    if len(args) == 0:
      self.x = 0
      self.y = 0
      return
    if len(args) == 1:
      self.x = self.y = args[0]
      return
    self.x, self.y = args

  def __add__(self, other):
    return Vector(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return Vector(self.x - other.x, self.y - other.y)

  def __mul__(self, n):
    return Vector(self.x*n, self.y*n)

  def __truediv__(self, n):
    return Vector(self.x/n, self.y/n)

  def __floordiv__(self, n):
    return Vector(self.x//n, self.y//n)

class KDNode:
  # constructor for KDNode
  # pos {Vector} position of node
  # axis {int} which axis the node splits space (0 splits x-axis, 1 splits y-axis)
  # left {KDNode} the left child node
  # right {KDNode} the right child node
  def __init__(self, pos, axis, left, right):
    self.pos = pos
    self.axis = axis
    self.left = left
    self.right = right
    g = id(self)*51234517%256
    self.color = (g, g, g)

  # creates tree from list of points
  # points {list}
  # return {KDNode}
  @staticmethod
  def create_tree(points, depth=0):
    # base case
    if len(points) == 0:
      return None
    axis = depth%2
    
    # sample points for estimating median
    sample = []
    sample_size = math.ceil(len(points)/(math.log(len(points), 10) + 1))
    for _ in range(sample_size):
      sample.append(points[random.randint(0, len(points) - 1)])

    # function returns x or y depending on this nodes axis
    axis_coord = None
    if axis == 0:
      axis_coord = lambda a: a.x
    else:
      axis_coord = lambda a: a.y
    
    sample.sort(key=axis_coord)
    median = sample[sample_size//2]

    # filter points left and right of median
    median_axis = axis_coord(median)
    left_of_median = list(filter(lambda a: axis_coord(a) < median_axis, points))
    right_of_median = list(filter(lambda a: axis_coord(a) >= median_axis and a != median, points))
    
    # make left and right subtrees
    left = KDNode.create_tree(left_of_median, depth + 1)
    right = KDNode.create_tree(right_of_median, depth + 1)

    return KDNode(median, axis, left, right)
    
  # finds the nearest neighbor of a point
  # point {Vector} the point to find the nearest neighbor of
  # return {tuple} (nearest neighbor {KDNode}, squared distance {float})
  def find_nn(self, point):
    smallest = (self.pos.x - point.x)**2 + (self.pos.y - point.y)**2
    nearest_neighbor = self
    if self.left == None and self.right == None:
      return nearest_neighbor, smallest

    # function returns x or y depending on this nodes axis
    axis_coord = None
    if self.axis == 0:
      axis_coord = lambda a: a.x
    else:
      axis_coord = lambda a: a.y

    # determine which subtree should be checked first
    first = self.left
    other = self.right
    if axis_coord(point) > axis_coord(self.pos):
      first = self.right
      other = self.left
    if first == None:
      first, other = other, first

    first_nn, first_smallest = first.find_nn(point)
    if first_smallest < smallest:
      smallest = first_smallest
      nearest_neighbor = first_nn

    # function for finding the distance to this nodes line that splits space
    axis_distance = None
    if self.axis == 0:
      axis_distance = lambda a, b: abs(a.y - b.y)
    else:
      axis_distance = lambda a, b: abs(a.x - b.x)

    if first_smallest > axis_distance(self.pos, first.pos) and other != None:
      other_nn, other_smallest = other.find_nn(point)
      if other_smallest < smallest:
        smallest = other_smallest
        nearest_neighbor = other_nn

    return nearest_neighbor, smallest

def main():
  width = 500
  height = 500
  img = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))
  draw = ImageDraw.Draw(img)
  
  points = []
  point_count = 100
  for _ in range(point_count):
    points.append(Vector(random.random()*width, random.random()*height))
  # draw.point(points, fill=(0, 0, 0))
  tree = KDNode.create_tree(points)

  for x in range(width):
    for y in range(height):
      nn, _ = tree.find_nn(Vector(x, y))
      draw.point(((x, y)), fill=nn.color)
  
  img.show()

if __name__ == "__main__":
  main()