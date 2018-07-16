import numpy as np
from energy import sparse_capy
class ising:

	def __init__(self, repvotes, demvotes, A, beta=2**20, target=1.0, steps=100):
		# vote totals
		self.repvotes = repvotes
		self.demvotes = demvotes

		# temperature
		self.beta = beta

		# adjacency matrix
		self.A = A

		self.target = target
		self.steps = steps
		
	def __iter__(self):
		self.counter = 0
		self.newrepvotes = np.array(self.repvotes)
		self.newdemvotes = np.array(self.demvotes)
		return self

	def __next__(self):
		'''
		iterator to give the next state in the ising_simulation
		'''
		if self.counter == self.steps:
			raise StopIteration
		self.counter += 1
		prop_rep, prop_dem = self.proposal(self.newrepvotes, self.newdemvotes)
		old_en = sparse_capy(self.newrepvotes, self.newdemvotes, self.A)
		new_en = sparse_capy(prop_rep, prop_dem, self.A)
		if (old_en < self.target):
			swap = self.accept(old_en, new_en, self.beta)
		else:
			swap = self.accept(new_en, old_en, self.beta)
		if swap:
			self.newrepvotes = prop_rep
			self.newdemvotes = prop_dem
		return self.newrepvotes, self.newdemvotes

	def accept(self, old, new, beta):
		'''
		metropolis hasting acceptance function for higher energies (i.e. always accept higher)
		old - old energy score
		new - new energy score

		### swap old and new to accept lower energies
		'''
		if new >= old:
			return True
		elif np.random.rand() < np.exp(-beta*(old-new)):
			return True
		else:
			return False
    
	def proposal(self, curr_rep, curr_dem):
		idx1 = 0
		idx2 = 0
		new_rep = np.array(curr_rep)
		new_dem = np.array(curr_dem)
		while idx1 == idx2:
			idx1 = np.random.randint(0,curr_rep.size-1)
			idx2 = np.random.randint(0,curr_dem.size-1)
		
		# number of people to swap
		max_num_swap = min(curr_rep[idx1], curr_dem[idx2])
		if max_num_swap > 1:
			num_swap = np.random.randint(1, max_num_swap)
		else:
			num_swap = 0
		new_rep[idx1] -= num_swap
		new_rep[idx2] += num_swap
		new_dem[idx1] += num_swap
		new_dem[idx2] -= num_swap
		return new_rep, new_dem

	def set_target(self, target):
		self.target = target
	
