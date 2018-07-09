# Code overview
There is currently a lot of excess, but the primary code is in the files that has "_graph" at the end of the name. These files will currently work with existing code only with graphs that have a number of nodes divisible by the number of districts you want. Additionally each node must be classified as either majority (1) or minority (-1), otherwise the way the ising model works will break and it is unclear what will happen. 

-- we might want to consider making a new folder in the repo for the real data code -- 


A brief outline of the code is below, and will have listed changes needed to be implemented necessary for our desired functionality.

## ising_energy_calculator_graph.py
This file contains the implementations for each energy score. Each score inherits from an abstract score and implements the functions necessary for use -- see the file for method descriptions. 

 ### What needs to be changed
 All the scores are currently designed with the notion that each node is either all minority or majority of equal population, needs to be updated for our new scores (i.e. x'(A+I)x / 2, happy capy, etc). Note that the current node makes reference to swapping two nodes, which no longer makes sense, but what may make sense is evaluating the delta in population and how that effects the score -- but this might not be any more efficient than recomputing the score which is much faster now anyways as its matrix multiplication. 

 ## districting_ensemble_generator_graph.py
 This file is essentially a mini chain that generates new districts and the initial seed district

 ### What needs to be changed
 This part should be replaced by actual RunDMCMC chain and integrated with the rest of the code. The trickiest part will be creating an initital district if one doesn't exist to use as a seed. For now we will have to rely on actualy districts as seeds, but when the spanning tree code is generalized to find equipartitions with weights, that can find seed districts. 

 ## ising_simulation_graph.py
 This file sets up the ising component where the population is moved around and initially distributed

 ### What needs to be changed
 Allow an input population configuration, and be able to setup a random configuration with nonbinary data and non uniform population, so you should have the number of each population at each node, although you will only be able to run ising on two populations at a time (unless if you use a nonbinary energy metric, might be able to vary all clusters but needs to be investigated). The metropolis-hastings step will need to be updated as the notion of adjacent nodes is different now

 ## main.py

 Basically just useful as to give an idea on how to interface with the code in its current format


