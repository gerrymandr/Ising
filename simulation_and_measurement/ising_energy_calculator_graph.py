from abc import ABC, abstractmethod
import math
import numpy as np
import numpy.linalg as la
import networkx as nx
import queue


class IsingEnergyCalculator(ABC):

    """Base class from which all energy calculators are built.
    Several possible energy types have calculators implemented below.

    Attributes
    ----------
    simulation : IsingSimulation
        simulation for which energy is being computed
    grid_size : int
        size of simulation grid
    """

    def __init__(self, ising_simulation):
        self.simulation = ising_simulation

    @abstractmethod
    def get_energy_diff_from_swap(self, v_minority, v_majority):
        """Get the energy change that results from swapping vertices.
        (assuming that they have opposite spins and are not adjacent)
        """
        pass

    @abstractmethod
    def get_total_energy():
        """Get the energy of the entire configuration."""
        pass

    @abstractmethod
    def get_energy_scale_factor():
        """Get rescaling factor so that energy scales linearly with edge count.
        This is used to prevent one from having to adjust the simulation
        temperature for every minority proportion and grid size.
        """
        pass


class HamiltonianEnergyCalculator(IsingEnergyCalculator):

    """Energy Calculator for the Ising model Hamiltonian
    H(config) = # edges between opposite spin vertices -
                # edges between same spin vertices
    low H -> high clustering
    high H -> low clustering
    """

    def get_energy_contribution(self, x):
        """Get the energy contribution of edges connected to vertex x = (i, j).
        """
        E = 0
        for nb in self.simulation.graph.neighbors(x):
            # minority-minority
            if self.simulation.config[nb] == self.simulation.config[x]:
                E += 1
            else:  # minority-majority
                E -= 1

        return -E

    def get_energy_diff_from_swap(self, v_minority, v_majority):
        """Get the energy change that results from swapping vertices.
        (assuming that they have opposite spins and aren't adjacent)
        """
        E_m = self.get_energy_contribution(v_minority)
        E_M = self.get_energy_contribution(v_majority)
        return -2 * (E_m + E_M)

    def get_total_energy(self):
        """Get the energy of the entire configuration."""
        E = 0
        for edge in self.simulation.edges:
            if self.simulation.config[edge[0]] == self.simulation.config[edge[1]]:
                E += 1
            else:
                E -= 1
        return -E

    def get_energy_scale_factor(self):
        # Hamiltonian energy already scales linearly with edge count
        return 1


class GammaEnergyCalculator(IsingEnergyCalculator):

    """Energy Calculator for our self-named Gamma Energy
    Gamma(config) = # edges between minority (-1 spin) vertices
    low G -> low minority clustering
    high G -> high minority clustering
    """

    def get_num_minority_neighbors(self, x):
        """Get the number of minority (spin -1) neighbors of vertex x = (i, j).
        """
        num_minority_neighbors = 0
        for nb in self.simulation.graph.neighbors(x):
            #print(nb, self.simulation.config[nb])
            if -1 == self.simulation.config[nb]:
                num_minority_neighbors += 1

        #print("num neighbors:", num_minority_neighbors)
        return num_minority_neighbors

    def get_energy_diff_from_swap(self, v_minority, v_majority):
        """Get the energy change that results from swapping vertices.
        (assuming that they have opposite spins and aren't adjacent)
        """
        #print("min:", v_minority)
        n_m = self.get_num_minority_neighbors(v_minority)
        n_M = self.get_num_minority_neighbors(v_majority)
        return n_M - n_m

    def get_total_energy(self):
        """Get the energy of the entire configuration."""
        x = np.array([self.simulation.config])
        x[x == 1] = 0
        M = nx.to_numpy_matrix(self.simulation.graph)
        E = np.matmul(x, np.matmul(M, x.T))/2

        return E[0,0]

    def get_energy_scale_factor(self):
        # gamma energy already scales linearly with edge count
        return 1


class NormalizedGammaEnergyCalculator(GammaEnergyCalculator):

    """Energy Calculator for a normalized variant of Gamma Energy
    Gamma*(config) = # edges between minority (-1 spin) vertices /
                     ~ max # possible for given minority count and grid size 
    G ~ 0 -> low minority clustering
    G ~ 1 -> high minority clustering
    """

    def __init__(self, ising_simulation):
        super().__init__(ising_simulation)
        # our maximum assumes all of the minority vertices are in a square, so
        # this is slight overestimate when minority count isn't perfect square
        self.max_gamma = self.get_max_gamma()

    def get_energy_diff_from_swap(self, v_minority, v_majority):
        """Get the energy change that results from swapping vertices.
        (assuming that they have opposite spins and aren't adjacent)
        """
        dE = super().get_energy_diff_from_swap(v_minority, v_majority)
        return dE / self.max_gamma

    def get_total_energy(self):
        """Get the energy of the entire configuration."""
        return super().get_total_energy() / self.max_gamma

    def get_energy_scale_factor(self):
        """Undo normalization to scale linearly with edge count."""
        return self.max_gamma

    def get_max_gamma(self):
        #maxeig = np.max(la.eig(nx.to_numpy_matrix(self.simulation.graph))[0])
        return 2 * math.sqrt(self.simulation.num_minority_vertices)\
            * (math.sqrt(self.simulation.num_minority_vertices) - 1)#np.real(maxeig) / self.simulation.num_minority_vertices


'''
class ConnectionProbabilityEnergyCalculator(IsingEnergyCalculator):
        
    """Energy Calculator for our self-named Gamma Energy
    CP(config) = # minority-minority edges / (total # minority edges)
    low CP -> low minority clustering
    high CP -> high minority clustering
    """
    
    def get_neighbor_classifications(self, x):
        """Get the number of minority and majority neighbors
        """
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
        """Get the energy change that results from swapping vertices.
        (assuming that they have opposite spins and aren't adjacent)
        """
        n_m = self.get_num_minority_neighbors(v_minority)
        n_M = self.get_num_minority_neighbors(v_majority)
        return n_M - n_m
    
    def get_total_energy(self):
        """Get the energy of the entire configuration."""
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
'''
