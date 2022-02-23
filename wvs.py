import math
import random
from PIL import Image, ImageDraw
import numpy as np

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
  def __init__(self, pos, left, right):
    self.pos = pos
    self.left = left
    self.right = right
    self.color = id(self)*51234517%256

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

    return KDNode(median, left, right)
    
  # finds the nearest neighbor of a point
  # point {Vector} the point to find the nearest neighbor of
  # return {tuple} (nearest neighbor {KDNode}, squared distance {float})
  def find_nn(self, point, depth):
    find_sq_dist = lambda a, b: (a.pos.x - b.pos.x)**2 + (a.pos.y - b.pos.y)**2
    self_sq_dist = find_sq_dist(self.pos, point)
    if self.left == None and self.left == None:
      return self_sq_dist, self
         

def main():
  width = 500
  height = 500
  img = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))
  
  points = []
  point_count = 100
  for _ in range(point_count):
    points.append(Vector(random.random()*width, random.random()*height))
  # draw.point(points, fill=(0, 0, 0))
  tree = KDNode.create_tree(points)

  pixels = np.empty([width, height], dtype=np.uint8)
  for x in range(width):
    for y in range(height):
      nn, _ = tree.find_nn(Vector(x, y))
      pixels[x, y] = nn.color
      # draw.point(((x, y)), fill=nn.color)
  img = Image.fromarray(pixels)
  img.show()

if __name__ == "__main__":
  main()
