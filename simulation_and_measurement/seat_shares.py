import numpy as np

def get_minority_seat_share(config, districting):
    """Get minority seat share for voter configuration wrt districting plan.
    
    Parameters
    ----------
    config : numpy.array (1 x num vertices)
        voter configuration from Ising simulation, -1 = minority
    districting : numpy.array(1 x num vertices)
        assignment of each vertex to a district label
            
    Returns
    -------
    seats : int
        # of districts in which minority voters have a majority           
    """
    num_districts = int(max(districting)) + 1
    seats = 0
    for d in range(num_districts):
        vote_diff = np.sum(config[districting == d])
        if vote_diff < 0:
            seats += 1
        # add half a seat in the case of a tie
        elif vote_diff == 0:
            seats += 0.5
    return seats

def get_expected_minority_seat_shares(configs, districting_ensemble):
    """Get expected minority seat shares for voter configurations wrt ensemble.
    
    Parameters
    ----------
    configs : list<numpy.array<{-1,1}> (grid size x grid size)>
        list of voter configurations from Ising simulation, -1 minority
    districting_ensemble: list<tuple<int> (1 x num vertices)>
        list of generated districting plans, where each is an assigment of
        vertices to district labels
        
    Returns
    -------
    expected_seat_shares : list<float>
        list of expected minority seat shares for each of the configurations
    """
    expected_seat_shares = []
    for config in configs:
        # get_seat_share takes to flat arrays, convert config from matrix
        config = config.flatten()
        expected_seat_share = 0
        for districting in districting_ensemble:
            # convert districting plan tuple into numpy array
            expected_seat_share += get_minority_seat_share(config,
                                                           np.array(districting))
        expected_seat_share /= len(districting_ensemble)
        expected_seat_shares.append(expected_seat_share)
    return expected_seat_shares