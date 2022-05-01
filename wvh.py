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

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y

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

    # base case
    if self.left == None and self.left == None:
      return self

    # determine subtree to check first
    first_subtree = self.right
    second_subtree = self.left
    if self.right == None or target.at_axis(axis) < self.pos.at_axis(axis):
      first_subtree = self.left
      second_subtree = self.right

    # check first subtree
    first_nn = first_subtree.find_nn(target, depth + 1)
    first_sq_dist = find_sq_dist(first_nn.pos, target)
    if first_sq_dist < best_sq_dist:
      best_sq_dist = first_sq_dist
      nn = first_nn

    # check second subtree if necessary
    axis_sq_dist = (first_nn.pos.at_axis(axis) - target.at_axis(axis))**2
    if second_subtree != None and axis_sq_dist < first_sq_dist:
      second_nn = second_subtree.find_nn(target, depth + 1)
      second_sq_dist = find_sq_dist(second_nn.pos, target)
      if second_sq_dist < best_sq_dist:
        best_sq_dist = second_sq_dist
        nn = second_nn

    return nn

  # gets a list of nodes in subtree
  # return {list} list of nodes
  def get_nodes(self):
    nodes = [self]
    if self.left != None:
      nodes += self.left.get_nodes()
    if self.right != None:
      nodes += self.right.get_nodes()
    return nodes

# creates a probability density function (ranges from 255 to 0. 255 in dark regions, 0 in light regions)
# pixels {list} the input image's pixels
# return {function} the probability density function
def get_pdf(pixels):
  def pdf(x, y):
    r, g, b = pixels[x, y]
    return 255 - (r + g + b)/3
  return pdf

# relaxes seeds (moves them to the weighted center of their site)
# tree {KDNode} the tree to be relaxed
# width {int} width of image
# height {int} height of image
# pdf {function} probability density function
# return {list} list of relaxed seeds
# return {list} list of densities for the seeds (0-1 normalized)
def relax_seeds(tree, width, height, pdf):
  vector_sums = {}
  weight_sums = {}
  totals = {}
  nodes = tree.get_nodes()
  for node in nodes:
    n = pdf(node.pos.x, node.pos.y)
    i = id(node)
    vector_sums[i] = node.pos*n
    weight_sums[i] = n
    totals[i] = 1
  for x in range(width):
    for y in range(height):
      nn = tree.find_nn(Vector(x, y))
      i = id(nn)
      if nn.pos == Vector(x, y):
        continue
      
      n = pdf(x, y)
      vector_sums[i] += Vector(x, y)*n
      weight_sums[i] += n
      totals[i] += 1
  points = []
  densities = []
  for s, w, t, in zip(vector_sums.values(), weight_sums.values(), totals.values()):
    if w == 0:
      w = 1
    points.append(s/w)
    densities.append(w/(t*255))

  return points, densities

# binary search
# arr {list} list of numbers
# item {float} item to search for
# return {float} the closest number (below) in the list to the item
def search(arr, item):
  if len(arr) == 1:
    return arr[0]
  mid = len(arr)//2
  if item > arr[mid]:
    return search(arr[mid:], item)
  elif item < arr[mid]:
    return search(arr[:mid], item)
  return item

# creates a list of random points, favoring points with a higher pdf score
# pdf {function} probability densitiy function 
# width {int} width of the image
# height {int} height of the image
# point_count {int} the desired amount of points
# return {list} list of sampled points
def importance_sampling(pdf, width, height, point_count):
  dictionary = {}
  for x in range(width):
    for y in range(height):
      intensity = pdf(x, y)
      if intensity in dictionary.keys():
        dictionary[intensity].append(Vector(x, y))
      else:
        dictionary[intensity] = [Vector(x, y)]
  points = []
  for i in range(point_count):
    rand = random.random()*32895
    intensity = math.floor((math.sqrt(1 + 8*rand) - 1)/2)
    
    key = search(list(dictionary.keys()), intensity)
    points.append(dictionary[key].pop())
    if dictionary[key] == []:
      del dictionary[key]
  return points

# draws points
# points {list} list of point to draw
# densities {list} list of densities of the points sites
# min_r {float} minimum radius the dots can be
# max_r {float} maximum radius the dots can be
# width {int} inputted picture's width
# height {int} inputted picture's height
# scale {float} how much bigger the displayed image should be than the inputted image
def draw(points, densities, min_r, max_r, width, height, scale):
  res = Image.new("RGB", (round(width*scale), round(height*scale)), (255, 255, 255))
  draw = ImageDraw.Draw(res)
  for point, density in zip(points, densities):
    r = (density - 1)*(max_r - min_r) + min_r
    bound = (point.x*scale - r, point.y*scale - r, point.x*scale + r, point.y*scale + r)
    draw.ellipse(bound, fill=(0, 0, 0))
  res.show()

def main():
  # read input picture
  with Image.open("picture.png") as input_img:
    input_pixels = input_img.load()
    width, height = input_img.size
  pdf = get_pdf(input_pixels)

  # initializes seeds
  point_count = int(input("point count: ")) # 10,000 recommended for colosseum picture
  points = importance_sampling(pdf, width, height, point_count)
  tree = KDNode.create_tree(points)

  # relaxes points
  iterations = int(input("iterations: ")) # 100 recommended for colosseum picture; you can stop it at any time
  min_r = int(input("minimum point radius: ")) # 4 recommended for colosseum picture
  max_r = int(input("minimum point radius: ")) # 7 recommended for colosseum picture
  for _ in range(iterations):
    points, densities = relax_seeds(tree, width, height, pdf)
    scale =  int(input("scale: ")) # 3 recommended for colosseum picture
    draw(points, densities, min_r, max_r, width, height, scale)
    tree = KDNode.create_tree(points)
if __name__ == "__main__":
  main()


# 1. put the picture that you want to halftone in the same folder as this script and name it “picture.png.”
# 2. run this script.
# 4. input values when prompted in the console. recommended values for the colosseum picture are 10000, 100, 4, 7, and 3, for point count, iterations, minimum point radius, maximum point radius, and scale respectively.
# each iteration will output a picture. stop the program when you’ve made it through all the iterations, or when you’re happy with the result.
