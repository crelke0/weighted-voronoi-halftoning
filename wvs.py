import math
import random
from PIL import Image

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

  # creates tree from list of points
  # points {list}
  # return {KDNode}
  @staticmethod
  def createTree(points, depth=0):
    # base case
    if len(points) == 0:
      return None
    axis = depth%2
    
    # sample points for estimating median
    sample = []
    sampleSize = len(points)//(math.log(10, len(points)) + 1)
    for _ in range(sampleSize):
      sample.append(points[random.randint(len(points))])

    # function returns x or y depending on this nodes axis
    axisCoord = None
    if axis == 0:
      axisCoord = lambda a: a.x
    else:
      axisCoord = lambda a: a.x
    
    sample.sort(key=axisCoord)
    median = sample[sampleSize//2]

    # filter points left and right of median
    medianAxis = axisCoord(median)
    leftOfMedian = list(filter(lambda a: axisCoord(a) < medianAxis))
    rightOfMedian = list(filter(lambda a: axisCoord(a) >= medianAxis and a != median))
    
    # make left and right subtrees
    left = KDNode.createTree(leftOfMedian, depth + 1)
    right = KDNode.createTree(rightOfMedian, depth + 1)

    return KDNode(median, axis, left, right)
    
  # finds the nearest neighbor of a point
  # point {Vector} the point to find the nearest neighbor of
  # return {tuple} (nearest neighbor {KDNode}, squared distance {float})
  def findNN(self, point):
    smallest = (self.pos.x - point.pos.x)**2 + (self.pos.y - point.pos.y)**2
    nearestNeighbor = self
    if self.left == None and self.right == None:
      return nearestNeighbor, smallest

    # function returns x or y depending on this nodes axis
    axisCoord = None
    if self.axis == 0:
      axisCoord = lambda a: a.x
    else:
      axisCoord = lambda a: a.y

    # determine which subtree should be checked first
    first = self.left
    other = self.right
    if axisCoord(point) > axisCoord(self.pos):
      first = self.right
      other = self.left
    if first == None:
      first, other = other, first

    firstNN, firstSmallest = first.findNN(point)
    if firstSmallest < smallest:
      smallest = firstSmallest
      nearestNeighbor = firstNN

      # function for finding the distance to this nodes line that splits space
    axisDistance = None
    if self.axis == 0:
      axisDistance = lambda a, b: abs(a.y - b.y)
    else:
      axisDistance = lambda a, b: abs(a.x - b.x)

    if firstSmallest > axisDistance(self.pos, first.pos) and other != None:
      otherNN, otherSmallest = other.findNN(point)
      if otherSmallest < smallest:
        smallest = otherSmallest
        nearestNeighbor = otherNN

    return nearestNeighbor, smallest

    

def main():
  pass

if __name__ == "__main__":
  main()