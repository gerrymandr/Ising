import copy
import numpy as np
import math
from ising_energy_calculator import HamiltonianEnergyCalculator,\
                                    GammaEnergyCalculator,\
                                    NormalizedGammaEnergyCalculator

class IsingSimulation:
    def __init__(self,
                 grid_size,
                 minority_proportion,
                 energy_type='normalized-gamma',
                 temperature=0.25):
        self.grid_size = grid_size
        self.num_vertices = grid_size ** 2
        self.minority_proportion = minority_proportion
        self.num_minority_vertices = \
            math.floor(self.num_vertices * minority_proportion)
        
        if energy_type == 'hamiltonian':
            self.energy_calculator = HamiltonianEnergyCalculator(self)
        elif energy_type == 'gamma':
            self.energy_calculator = GammaEnergyCalculator(self)
        elif energy_type == 'normalized-gamma':
            self.energy_calculator = NormalizedGammaEnergyCalculator(self)
        else:
            raise ValueError('invalid energy type: ' + str(energy_type))
        
        self.randomize_config()
        self.temperature = temperature
        
    def randomize_config(self):
        # create n x n grid with n^2*p random nodes assigned -1 and the rest 1
        # also computes the configuration's energy
        C = np.ones(self.num_vertices)
        C[1:self.num_minority_vertices] = -1
        np.random.shuffle(C)
        self.config = C.reshape((self.grid_size, self.grid_size))
        self.energy = self.energy_calculator.get_total_energy()
        (minority_rows, minority_cols) = np.where(self.config == -1)
        (majority_rows, majority_cols) = np.where(self.config == 1)
        self.minority_vertices = list(zip(minority_rows, minority_cols))
        self.majority_vertices = list(zip(majority_rows, majority_cols))
        
    def swap(self, v_minority, v_majority):
        # swap spins of vertices x and y and updates vertex lists
        # assuming that the spins are opposite
        self.minority_vertices.remove(v_minority)
        self.majority_vertices.append(v_minority)
        self.majority_vertices.remove(v_majority)
        self.minority_vertices.append(v_majority)
        
        (i1, j1) = v_minority
        (i2, j2) = v_majority
        self.config[v_minority[0], v_minority[1]] = 1
        self.config[v_majority[0], v_majority[1]] = -1
    
    def are_adjacent(self, x, y):
        # check if two vertices are adjacent (or the same),
        # uses rook adjacency on grid graph
        di = abs(x[0] - y[0])
        dj = abs(x[1] - y[1])
        return di + dj < 2
        
    def metropolis_step(self, energy_target):
        # perform Metropolis-Hastings step
        # seeks to minimize energy if above target
        # seeks to maximize energy if below target
        r1 = np.random.randint(len(self.minority_vertices))
        r2 = np.random.randint(len(self.majority_vertices))
        v_minority = self.minority_vertices[r1]
        v_majority = self.majority_vertices[r2]
        if self.are_adjacent(v_minority, v_majority):
            # retry if two positions are adjacent, to keep math concise
            return self.metropolis_step(energy_target)
        
        dE = self.energy_calculator.get_energy_diff_from_swap(v_minority,
                                                              v_majority)
        scaled_dE = dE * self.energy_calculator.get_energy_scale_factor()
        diff_from_target = energy_target - self.energy
        do_swap = False
        if diff_from_target <= 0:
            if dE <= 0 or \
               np.random.rand() < math.exp(-scaled_dE / self.temperature):
                do_swap = True
        else:
            if dE >= 0 or \
               np.random.rand() < math.exp(scaled_dE / self.temperature):
                do_swap = True
    
        if do_swap:
            self.swap(v_minority, v_majority)
            self.energy += dE
            pass
            
def generate_voter_configurations_with_energies(
    grid_size,
    minority_proportion,
    energy_type='normalized-gamma',
    energy_range=np.linspace(0, 1, num=20),
    temperature=0.25,
    num_initial_iterations=1000,
    num_samples_per_energy=40,
    iterations_between_samples=100
):
    simulation = IsingSimulation(grid_size,
                                 minority_proportion,
                                 energy_type,
                                 temperature)
    configs = []
    energies = []

    for energy_target in energy_range:
        simulation.randomize_config()
        for i in range(num_initial_iterations):
            simulation.metropolis_step(energy_target)
        for i in range(num_samples_per_energy):
            for j in range(iterations_between_samples):
                simulation.metropolis_step(energy_target)
            configs.append(copy.deepcopy(simulation.config))
            energies.append(simulation.energy)
    return (configs, energies)