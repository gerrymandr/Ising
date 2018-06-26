from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

def generate_animation(x_info, y_info, t_info, comparison_line_info,
                       best_fit_line_info, title, duration, outfile):
    """Generate moving cross section animation, along t-axis.
    
    Parameters
    ----------
    x_info : dict
        values, limits, and label for x-coordinates
        e.g. {'values': [0, 1, 2], 'limits': [0, 2], 'label': 'x'}
    y_info : dict
        values, limits, and label for y-coordinates
    t_info : dict
        values, label, range, and cross section width for t-coordinates, e.g.
        {
            'values': [0, 10],
            'label': 't',
            'range': range(10),
            'cross_section_width': 0
        }
    comparison_line_info : dict | None
        get_points(t) function and label for optional comparison line, e.g.
        {
            'get_points': lambda t: [[0, 1, 2], [3, 4, 5]],
            'label': 'Comparison Line'
        }
    best_fit_line_info : dict | None
        get_points(displayed_points_x, displayed_points_y) function and label
        for optional best fit line, e.g.
        {
            'get_points': lambda x,y: [[0, 1, 2], [3, 4, 5]],
            'label': 'Best Fit Line'
        }
    title : str
        title of plot
    duration : float
        duration of the animation, in seconds
    outfile : str | None
        optional file to which to save the animation
        
    Returns
    -------
    anim: matplotlib.animation.FuncAnimation
        animation object, reference must be stored in order for animation to
        show up on plot, i.e. save the result to a variable
    """
    # set up plot with limits, axis labels, and title
    fig = plt.figure()
    ax = plt.axes(xlim=x_info['limits'], ylim=y_info['limits'])
    ax.set_xlabel(x_info['label'])
    ax.set_ylabel(y_info['label'])
    ax.set_title(title)
    
    # create components to appear on plot
    t_text = ax.text(0.98, 0.95, '', transform=ax.transAxes,
                     horizontalalignment='right')
    scat = ax.scatter([], [], marker='.')
    
    # extract data needed for animation
    x = x_info['values']
    y = y_info['values']
    t = t_info['values']
    t_range = t_info['range']
    width = t_info['cross_section_width']
    
    # set up comparison and best fit lines with legend
    comparison_line, = ax.plot([], [], color='g')
    best_fit_line, = ax.plot([], [], color='r')
    legend_labels = []
    if comparison_line_info != None:
        get_comparison_line_points = comparison_line_info['get_points']
        legend_labels.append(comparison_line_info['label'])
    if best_fit_line_info != None:
        get_best_fit_line_points = best_fit_line_info['get_points']
        legend_labels.append(best_fit_line_info['label'])
    legend = ax.legend(legend_labels, loc='upper left')
    
    # define animation function which updates the plot
    def animate(i):
        # determine which points are in current t-axis cross section
        current_t = t_range[i]
        displayed_indices = [j for j in range(len(t)) \
             if (t[j] >= current_t) and (t[j] <= current_t + width)]
        x_disp = [x[j] for j in displayed_indices]
        y_disp = [y[j] for j in displayed_indices]
        
        # update points on scatter plot
        pts = np.array(list(zip(x_disp, y_disp)))
        if len(pts) == 0:
            pts = np.zeros((0,2))
        scat.set_offsets(pts)
        
        # update comparison line and best fit line, if present
        if comparison_line_info != None:
            comparison_line.set_data(get_comparison_line_points(current_t))
        if best_fit_line_info != None:
            best_fit_line.set_data(get_best_fit_line_points(x_disp, y_disp))
        
        # update text describing current state in time
        if width == 0:
            txt = '%s = %0.2f' % (t_info['label'], current_t)
        else:
            txt = '%s between %0.2f and %0.2f' % (t_info['label'],
                                                  current_t, current_t + width)
        t_text.set_text(txt)
        
        return scat, comparison_line, best_fit_line, t_text, legend

    # determine time b/t frames and create animation, saving if necessary
    interval = duration * 1000 / (len(t_range) - 1)
    anim = animation.FuncAnimation(fig, animate,
                                   frames=len(t_range),
                                   interval=interval, blit=True)
    if outfile != None:
        anim.save(outfile, fps=15, extra_args=['-vcodec', 'libx264'])
    return anim

def get_coordinate_info_from_data_tuples(data):
    """Transform data tuples into usable coordinate info objects."""
    proportions = []
    energies = []
    seats = []
    for point in data:
        # omitting first coordinate, which stores Ising configuration
        proportions.append(point[1])
        energies.append(point[2])
        seats.append(point[3])
    
    p_info = {'values': proportions, 'label': 'Minority Proportion'}
    e_info = {'values': energies, 'label': 'Energy'}
    s_info = {'values': seats, 'label': 'Expected # Seats Won'}
    return (p_info, e_info, s_info)

def generate_energy_seats_curve_animation(data, num_districts,
                                          energy_limits, expected_seats_limits,
                                          duration=5.0, outfile=None):
    """Generate energy-seats curve animated across proportion axis.
    
    Parameters
    ----------
    data : list<(Ising config, minority proportion, energy, expected seats)>
        list of data points representing individual configurations
    num_districts : int
        # of districts used for expected seats calculation
    energy_limits : [upper, lower]
        bounds on energy (x) axis for plot
    expected_seats_limits : [lower, upper]
        bounds on expected seats (y) axis for plot
    duration : float
        duration of the animation, in seconds
    outfile : str | None
        optional file to which to save the animation

    Returns
    -------
    anim: matplotlib.animation.FuncAnimation
        animation object, reference must be stored in order for animation to
        show up on plot, i.e. save the result to a variable
    """
    # declare coordinate data
    (p_info, e_info, s_info) = get_coordinate_info_from_data_tuples(data)
    e_info['limits'] = energy_limits
    s_info['limits'] = expected_seats_limits
    p_info['range'] = list(sorted(set(p_info['values']))) # unique proportions
    p_info['cross_section_width'] = 0
    
    # flat comparison line
    def get_comparison_line_points(p):
        e = np.linspace(energy_limits[0], energy_limits[1], 2)
        s = [num_districts * p, num_districts * p]
        return (e, s)
    comparison_line_info = {
        'get_points': get_comparison_line_points,
        'label': 'Proportional Representation'
    }
    
    return generate_animation(e_info, s_info, p_info,
                              comparison_line_info, None,
                              'Energy-Seats Curves at Varied Minority Proportion Levels',
                              duration, outfile)
    
def generate_votes_seats_curve_animation(data, num_districts,
                                         minority_proportion_limits,
                                         expected_seats_limits, energy_limits,
                                         energy_cross_section_width=0.05,
                                         num_frames=100, duration=5.0,
                                         outfile=None):
    """Generate votes-seats curve animated across energy axis.
    
    Parameters
    ----------
    data : list<(Ising config, minority proportion, energy, expected seats)>
        list of data points representing individual configurations
    num_districts : int
        # of districts used for expected seats calculation
    minority_proportion_limits : [lower, upper]
        bounds on minority proportion (x) axis for plot
    expected_seats_limits : [lower, upper]
        bounds on expected seats (y) axis for plot
    energy_limits : [lower, upper]
        bounds on energy (time) axis for plot
    energy_cross_section_width : float
        specify the level with which to inflate the cross sections in the
        energy axis, necessary so that they contain multiple points
    num_frames : int
        # of frames in animation
    duration : float
        duration of the animation, in seconds
    outfile : str | None
        optional file to which to save the animation
        
    Returns
    -------
    anim: matplotlib.animation.FuncAnimation
        animation object, reference must be stored in order for animation to
        show up on plot, i.e. save the result to a variable
    """
    # declare coordinate data
    (p_info, e_info, s_info) = get_coordinate_info_from_data_tuples(data)
    p_info['limits'] = minority_proportion_limits
    s_info['limits'] = expected_seats_limits
    e_info['range'] = np.linspace(energy_limits[0],
                                  energy_limits[1] - energy_cross_section_width,
                                  num_frames)
    e_info['cross_section_width'] = energy_cross_section_width
    
    # diagonal comparison line
    def get_comparison_line_points(e):
        p = np.linspace(minority_proportion_limits[0], minority_proportion_limits[1], 1000)
        s = p * num_districts
        return (p, s)
    comparison_line_info = {
        'get_points': get_comparison_line_points,
        'label': 'Proportional Representation'
    }
    
    # naive best fit line which takes the average seat share at each district
    # minority proportion level
    def get_best_fit_line_points(p, s):
        unique_proportions = list(sorted(set(p)))
        averaged_seats = []
        for p2 in unique_proportions:
           J = [j for j in range(len(p)) if p[j] == p2]
           seats = [s[j] for j in J]
           averaged_seats.append(sum(seats)/len(seats))
        return (unique_proportions, averaged_seats)
    best_fit_line_info = {
        'get_points': get_best_fit_line_points,
        'label': 'Current Votes-Seats Curve'
    }
    
    return generate_animation(p_info, s_info, e_info,
                              comparison_line_info, best_fit_line_info,
                              'Votes-Seats Curves at Varied Energy Levels',
                              duration, outfile)

#anim = generate_energy_seats_curve_animation(points2, 6, [0, 1], [0, 4], 10.0) 
anim = generate_votes_seats_curve_animation(points2, 6, [0, 0.5], [0, 3.5],
                                            [0, 1], 0.05, 100, 5.0)