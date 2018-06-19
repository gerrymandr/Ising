README file for _n_by_n_v2


The files in this directory contain all the files used to create districting plans on an 18x18 grid.

The output represents 5 runs of the program n_by_n.py, each of which generated ~30,000 districting plans. For each run, the number of seats won by Party 1 was calculated under 3 different distributions of Party 1 voters. In each distribution, Party 1 represented 31% of the population. 


Description of files: 

n_by_n.py
The python program that generates the random walk. 
It writes the list of unique districting plans to an output file specified in the program.
This program should work for any size grid and any number of districts. 

18x18_districts_rectanges.csv
Contains the initial districting used as the seed for the random walk.

party1_districting_counts.py
The python program that takes the output file from n_by_n.py and counts the number of districts won by Party 1 in each districting plan under a particular distribution of Party 1 voters in the grid. If the district gives a tie, then Party 1 is given 0.5 seats for this district. 

18x18_parties_clustered.csv
18x18_parties_striped.csv
18x18_parties_uniform.csv
These three files contain the different distributions of Party 1 in the grid. 
In each case, Party 1 has 31% of the total population in the district. 

summary_totals.pdf
summary_percents.pdf
summary.xlsx
These files contain a summary of the results for the 5 runs under each distribution.

output.xlsx
This single Excel file contains all from the 15 runs of party1_districting_counts.py. 
Note it is extremely large. 

raw_output/
Folder contains the output files from n_by_n.py and party1_districting_counts.py

build_csv.xlsx
Auxiliary spreadsheet used to build the csv files for the districting seed and Party 1 distributions. 

18x18_districts_final,pdf
For purely informational purposes, this shows the last districting plan generated in one of the random walks from _n_by_n_v1. 


