from PIL import Image

class Vector:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

class KDNode:
  def __init__(self, pos, axis, left, right):
    self.pos = pos
    self.axis = axis
    self.left = left
    self.right = right
      

def main():
  pass

if __name__ == "__main__":
  main()