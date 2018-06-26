from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

def generate_votes_seats_curve_animation(data,
                                         minority_proportion_limits,
                                         expected_seats_limits,
                                         energy_limits,
                                         duration=5.0,
                                         outfile=None):
    p = [] # minority proportion
    e = [] # energy (normalized gamma)
    s = [] # expected seats
    for point in data:
        p.append(point[1])
        e.append(point[2])
        s.append(point[3])
        
    fig = plt.figure()
    ax = plt.axes(xlim=minority_proportion_limits, ylim=expected_seats_limits)
    ax.set_xlabel('Energy')
    ax.set_ylabel('Expected Number of Seats')
    ax.set_title('Energy-Seats Curve at Varied Minority Proportion Levels')
    
    minority_proportion_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    scat = ax.scatter([], [], marker='.')
    line, = ax.plot([], [], lw=2, color='r')
        
    unique_probs = list(sorted(set(p)))
    
    def init():
        line.set_data([0, 0], [0.1, 0.2])
        return scat, line, minority_proportion_text
    
    def animate(i):
        I = [j for j in range(len(p)) if p[j] == unique_probs[i]]
        E = [e[i] for i in I]
        S = [s[i] for i in I]
        pts = np.array(list(zip(E,S)))
        if len(pts) == 0:
            pts = np.zeros((0,2))
        scat.set_offsets(pts)
        minority_proportion_text.set_text('Minority proportion = {:0.2f}'.format(
            unique_probs[i]))
        return scat, line, minority_proportion_text

    interval=duration*1000/(len(unique_probs)-1)
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=len(unique_probs),
                                   interval=interval, blit=True)
    if outfile != None:
        anim.save(outfile, fps=15, extra_args=['-vcodec', 'libx264'])
    return anim

anim = generate_votes_seats_curve_animation(points,
                                            [0, 1],
                                            [0, 4],
                                            [0, 1], 10.0, 'energy-seats.mp4')