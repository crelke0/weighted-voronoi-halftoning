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

  def at_axis(self, axis):
    return self.x if axis == 0 else self.y

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
  def find_nn(self, target, depth=0):
    axis = depth%2
    find_sq_dist = lambda a, b: (a.x - b.x)**2 + (a.y - b.y)**2
    best_sq_dist = find_sq_dist(self.pos, target)
    nn = self
    if self.left == None and self.left == None:
      return self
    first_subtree = self.right
    second_subtree = self.left
    if self.right == None or target.at_axis(axis) < self.pos.at_axis(axis):
      first_subtree = self.left
      second_subtree = self.right

    first_nn = first_subtree.find_nn(target, depth + 1)
    first_sq_dist = find_sq_dist(first_nn.pos, target)
    if first_sq_dist < best_sq_dist:
      best_sq_dist = first_sq_dist
      nn = first_nn

    axis_sq_dist = (first_nn.pos.at_axis(axis) - target.at_axis(axis))**2
    if second_subtree != None and axis_sq_dist < first_sq_dist:
      second_nn = second_subtree.find_nn(target, depth + 1)
      second_sq_dist = find_sq_dist(second_nn.pos, target)
      if second_sq_dist < best_sq_dist:
        best_sq_dist = second_sq_dist
        nn = second_nn

    return nn

def get_pdf(pixels):
  def pdf(x, y):
    r, g, b = pixels[x, y]
    return 1 - (r + g + b)/765
  return pdf

def relax_points(tree, width, height, pdf):
  sums = {}
  counts = {}
  for x in range(width):
    for y in range(height):
      nn = tree.find_nn(Vector(x, y))
      i = id(nn)
      if i not in sums.keys():
        sums[i] = Vector(0, 0)
        counts[i] = 0
      sums[i] += Vector(x, y)*pdf(x, y)
      counts[i] += 1
  points = []
  for sv, cv in zip(sums.values(), counts.values()):
    points.append(sv/cv)
  return KDNode.create_tree(points)

def main():
  with Image.open("picture.png") as input_img:
    input_pixels = input_img.load()
    width, height = input_img.size
  pdf = get_pdf(input_pixels)
  points = []
  point_count = 100
  for _ in range(point_count):
    points.append(Vector(random.random()*width, random.random()*height))
  tree = KDNode.create_tree(points)
  tree = relax_points(tree, width, height, pdf)


  # pixels = np.empty([width, height], dtype=np.uint8)
  # for x in range(width):
  #   for y in range(height):
  #     nn = tree.find_nn(Vector(x, y))
  #     pixels[x, y] = nn.color
  # res = Image.fromarray(pixels)
  # res.show()

if __name__ == "__main__":
  main()
