from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

def generate_votes_seats_curve_animation(data,
                                         minority_proportion_limits,
                                         expected_seats_limits,
                                         energy_limits,
                                         energy_cross_section_width=0.05,
                                         num_frames=100,
                                         duration=5.0,
                                         outfile=None):
    p = [] # minority proportion
    s = [] # expected seats
    e = [] # energy (normalized gamma)
    for point in data:
        p.append(point[1])
        s.append(point[3])
        e.append(point[2])
        
    fig = plt.figure()
    ax = plt.axes(xlim=minority_proportion_limits, ylim=expected_seats_limits)
    ax.set_xlabel('Minority Proportion')
    ax.set_ylabel('Expected Number of Seats')
    ax.set_title('Votes-Seats Curve at Varied Energy Levels')
    
    
    energy_text = ax.text(0.02, 0.8, '', transform=ax.transAxes)
    scat = ax.scatter([], [], marker='.')
    line, = ax.plot([], [], lw=2, color='r')
    x2 = np.linspace(minority_proportion_limits[0],
                     minority_proportion_limits[1], 1000)
    y2 = x2*6
    ax.plot(x2, y2, color='g')
    legend = ax.legend(['Current Votes-Seats Curve', 'Proportional Representation'], loc='upper left')

    energy_lower_start = energy_limits[0]
    energy_lower_stop = energy_limits[1] - energy_cross_section_width
    energy_lower_step = \
        (energy_lower_stop - energy_lower_start) / (num_frames - 1)
    
    def init():
        line.set_data([], [])
        return scat, line, legend, energy_text
    
    def animate(i):
        lower = energy_lower_start + i*energy_lower_step
        I = [i for i in range(len(e)) \
             if lower < e[i] < lower + energy_cross_section_width]
        P = [p[i] for i in I]
        S = [s[i] for i in I]
        pts = np.array(list(zip(P,S)))
        if len(pts) == 0:
            pts = np.zeros((0,2))
        scat.set_offsets(pts)
        unique_probs = list(sorted(set(P)))
        averaged_seats = []
        for pp in unique_probs:
           J = [j for j in range(len(P)) if P[j] == pp]
           seats = [S[j] for j in J]
           averaged_seats.append(sum(seats)/len(seats))
        line.set_data(unique_probs, averaged_seats)
        energy_text.set_text('Energy between {:0.2f} and {:0.2f}'.format(
            lower, lower + energy_cross_section_width))
        return scat, line, legend, energy_text

    interval=duration*1000/(num_frames-1)
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=num_frames,
                                   interval=interval, blit=True)
    if outfile != None:
        anim.save(outfile, fps=15, extra_args=['-vcodec', 'libx264'])
    return anim

anim = generate_votes_seats_curve_animation(points,
                                            [0, 0.5],
                                            [0, 3.5],
                                            [0, 1], 0.05, 100, 5.0, 'test.mp4')