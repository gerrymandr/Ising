import pandas as pd
import numpy as np
rook_4x4 = pd.read_csv("../data/4x4partitions.csv", header=None)

def get_graph(n):
  start = n*4
  end = (n+1)*4
  return rook_4x4[start:end]

def get_meta():
  meta = np.load("../results/meta_adj_110_from_4x4partitions.npy")
  print (meta)
  return meta


