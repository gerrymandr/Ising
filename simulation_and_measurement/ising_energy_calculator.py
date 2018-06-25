from abc import ABC, abstractmethod
import math

class IsingEnergyCalculator(ABC):
    def __init__(self, ising_simulation):
        self.simulation = ising_simulation
        self.grid_size = ising_simulation.grid_size
    
    @abstractmethod
    def get_energy_diff_from_swap(self, v_minority, v_majority):
        # get the energy change that results from swapping vertices
        # assuming that they have opposite spins
        pass
    
    @abstractmethod
    def get_total_energy():
        # get the energy of the entire configuration
        pass
    
    @abstractmethod
    def get_energy_scale_factor():
        # rescaling coefficient so that energy scales linearly with edge count
        pass

class HamiltonianEnergyCalculator(IsingEnergyCalculator):
    def get_energy_contribution(self, x):
        # get the energy contribution of edges connected to vertex x = (i, j),
        # according to Ising model Hamiltonian
        i = x[0]
        j = x[1]
        up    = self.simulation.config[i-1, j] if (i > 0) else 0
        down  = self.simulation.config[i+1, j] if (i < self.grid_size-1) else 0
        left  = self.simulation.config[i, j-1] if (j > 0) else 0
        right = self.simulation.config[i, j+1] if (j < self.grid_size-1) else 0
        sum_of_neighbors = up + down + left + right
        return -self.simulation.config[i, j] * sum_of_neighbors
    
    def get_energy_diff_from_swap(self, v_minority, v_majority):
        # get the energy change that results from swapping vertices
        # assuming that they have opposite spins
        E_m = self.get_energy_contribution(v_minority)
        E_M = self.get_energy_contribution(v_majority)
        return -2 * (E_m + E_M)
    
    def get_total_energy(self):
        # get the energy of the entire configuration,
        # according to Ising model Hamiltonian
        E = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                E += self.get_energy_contribution((i, j)) / 2
                # / 2 necessary since each edge is counted twice
        return E
    
    def get_energy_scale_factor(self):
        # Hamiltonian energy already scales linearly with edge count
        return 1
    
class GammaEnergyCalculator(IsingEnergyCalculator):
    def get_num_minority_neighbors(self, x):
        # get the number of minority (spin -1) neighbors of vertex x
        i = x[0]
        j = x[1]
        up    = self.simulation.config[i-1, j] if (i > 0) else 0
        down  = self.simulation.config[i+1, j] if (i < self.grid_size-1) else 0
        left  = self.simulation.config[i, j-1] if (j > 0) else 0
        right = self.simulation.config[i, j+1] if (j < self.grid_size-1) else 0
        num_minority_neighbors = (1 if up == -1 else 0) + \
                                 (1 if down == -1 else 0) + \
                                 (1 if left == -1 else 0) + \
                                 (1 if right == -1 else 0)
        return num_minority_neighbors
    
    def get_energy_diff_from_swap(self, v_minority, v_majority):
        # get the energy change that results from swapping vertices
        # assuming that they have opposite spins
        n_m = self.get_num_minority_neighbors(v_minority)
        n_M = self.get_num_minority_neighbors(v_majority)
        return n_M - n_m
    
    def get_total_energy(self):
        # get the energy of the entire configuration,
        # according to gamma energy
        # w/ gamma(system) = # edges b/t minority vertices
        E = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                spin = self.simulation.config[i, j]
                if spin == -1:
                    E += self.get_num_minority_neighbors((i, j)) / 2
                # / 2 necessary since each edge is counted twice
        return E
    
    def get_energy_scale_factor(self):
        # gamma energy already scales linearly with edge count
        return 1
    
class NormalizedGammaEnergyCalculator(GammaEnergyCalculator):
    def __init__(self, ising_simulation):
        super().__init__(ising_simulation)
        square_size = \
            math.ceil(math.sqrt(ising_simulation.num_minority_vertices))
        self.max_gamma = 2  * square_size * (square_size - 1)
        
    def get_energy_diff_from_swap(self, v_minority, v_majority):
        dE = super().get_energy_diff_from_swap(v_minority, v_majority)
        return dE  / self.max_gamma
    
    def get_total_energy(self):
        return super().get_total_energy() / self.max_gamma
    
    def get_energy_scale_factor(self):
        # undo normalization to scale linearly with edge count
        return self.max_gamma
    