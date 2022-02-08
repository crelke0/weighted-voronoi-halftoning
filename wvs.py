import math
import random
from PIL import Image

class Vector:
  # constructor for Vector
  # lst {list} the list of values for the axis (can be length 0, 1, or 2)
  def __init__(self, lst=None):
    if lst == None:
      self.x = 0
      self.y = 0
      return
    if len(lst) == 1:
      self.x = self.y = lst[0]
      return
    self.x, self.y = lst

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
    
    # estimate median
    sample = []
    sampleSize = len(points)//(math.log(10, len(points)) + 1)
    for _ in range(sampleSize):
      sample.append(points[random.randint(len(points))])
    getAxis = None
    if axis == 0:
      getAxis = lambda a: a.x
    else:
      getAxis = lambda a: a.x
    sample.sort(key=getAxis)
    median = sample[sampleSize//2]

    # filter points left and right of median
    medianAxis = getAxis(median)
    leftOfMedian = list(filter(lambda a: getAxis(a) < medianAxis))
    rightOfMedian = list(filter(lambda a: getAxis(a) >= medianAxis and a != median))
    
    # make left and right subtrees
    left = KDNode.createTree(leftOfMedian, depth + 1)
    right = KDNode.createTree(rightOfMedian, depth + 1)

    return KDNode(median, axis, left, right)
      

def main():
  pass

if __name__ == "__main__":
  main()