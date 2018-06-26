import copy
import numpy as np
import math
from ising_energy_calculator import HamiltonianEnergyCalculator,\
                                    GammaEnergyCalculator,\
                                    NormalizedGammaEnergyCalculator

class IsingSimulation:
    
    """Stores Ising configuration and updates it via Metropolis-Hastings.
    
    Attributes
    ----------
    grid_size : int
        width/height of grid graph underlying simulation
    num_vertices : int
        # of vertices in grid graph
    minority_proportion : float
        proportion of spin -1 vertices which represent minority group
    num_minority_vertices : int
        # of spin -1 vertices which represent minority group
    temperature : float
        level of randomness to introduce into Metropolis-Hastings
    config : numpy.array<{-1, 1}> (grid_size x grid_size)
        state storing spin of each vertex in grid graph
    energy_calculator : IsingEnergyCalculator
        object which performs energy calculations for simulation
    energy : float
        energy value of configuration, according to selected energy type
    minority_vertices : list<(int, int)>
        list of minority vertex locations
    majority_vertices : list<(int, int)>
        list of majority vertex locations
    """
    
    def __init__(self,
                 grid_size,
                 minority_proportion,
                 energy_type='normalized-gamma',
                 temperature=0.25):
        """Initialize simulation.
        
        Parameters
        ----------
        energy_type : 'hamiltonian' | 'gamma' | 'normalized-gamma'
            type of energy to use for simulation
        See class docstring for other details.
        """
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
        """Initialize with random configuration and compute its energy.
        n^2*p random nodes are assigned to -1 and the rest to 1.
        """
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
        """Swap spins of vertices x and y and updates vertex lists.
        (assuming that the spins are opposite)
        """
        self.minority_vertices.remove(v_minority)
        self.majority_vertices.append(v_minority)
        self.majority_vertices.remove(v_majority)
        self.minority_vertices.append(v_majority)
        
        (i1, j1) = v_minority
        (i2, j2) = v_majority
        self.config[v_minority[0], v_minority[1]] = 1
        self.config[v_majority[0], v_majority[1]] = -1
    
    def are_adjacent(self, x, y):
        """Check if two vertices are adjacent or the same.
        (using rook adjacency on the grid graph)
        """
        di = abs(x[0] - y[0])
        dj = abs(x[1] - y[1])
        return di + dj < 2
        
    def metropolis_step(self, target_energy):
        """Perform Metropolis-Hastings step, moving towards target energy.
        - seeks to minimize energy if above target
        - seeks to maximize energy if below target
        """
        r1 = np.random.randint(len(self.minority_vertices))
        r2 = np.random.randint(len(self.majority_vertices))
        v_minority = self.minority_vertices[r1]
        v_majority = self.majority_vertices[r2]
        if self.are_adjacent(v_minority, v_majority):
            # retry if two positions are adjacent, to keep math concise
            return self.metropolis_step(target_energy)
        
        dE = self.energy_calculator.get_energy_diff_from_swap(v_minority,
                                                              v_majority)
        # scale dE so that it's consistent between different energy types
        scaled_dE = dE * self.energy_calculator.get_energy_scale_factor()
        diff_from_target = target_energy - self.energy
        do_swap = False
        # move down if above target energy
        if diff_from_target <= 0:
            if dE <= 0 or \
               np.random.rand() < math.exp(-scaled_dE / self.temperature):
                do_swap = True
        # move up if below target energy
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
    target_energy_range=np.linspace(0, 1, num=20),
    temperature=0.25,
    num_initial_iterations=1000,
    num_samples_per_energy=40,
    num_iterations_between_samples=100
):
    """Generate voter configurations and energies given target energy range.
    
    Parameters
    ----------
    grid_size : int
        width/height of grid graph underlying simulation
    minority_proportion : float
        proportion of spin -1 vertices which represent minority group
    energy_type : 'hamiltonian' | 'gamma' | 'normalized-gamma'
        type of energy to use for simulation
    target_energy_range : np.array<float>
        list of target energies
    temperature : float
        level of randomness to introduce into simulation
    num_initial_iterations : int
        # of initial simulation steps to take before sampling configurations
    num_samples_per_energy : int
        # of configurations to sample for each target energy
    num_iterations_between_samples : int
        # of interations to run between samples for each target energy
    """
    simulation = IsingSimulation(grid_size,
                                 minority_proportion,
                                 energy_type,
                                 temperature)
    configs = []
    energies = []

    for target_energy in target_energy_range:
        simulation.randomize_config()
        for i in range(num_initial_iterations):
            simulation.metropolis_step(target_energy)
        for i in range(num_samples_per_energy):
            for j in range(num_iterations_between_samples):
                simulation.metropolis_step(target_energy)
            configs.append(copy.deepcopy(simulation.config))
            energies.append(simulation.energy)
    return (configs, energies)