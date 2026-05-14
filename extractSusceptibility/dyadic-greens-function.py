import numpy as np
import matplotlib.pyplot as plt

#def scalar_greens_function(k,R,R0):

def drawBound(ax, xDom, yDom, xMin=0, yMin=0, xB=20, yB=20, c='red', l='', z=-2):
    #ax.fill([-xB, xDom+xB, xDom+xB, -xB], [-yB, -yB, yDom+yB, yDom+yB], color=c, zorder=z, label=l)
    ax.fill_between([-xB,xDom+xB], [yMin, yMin],[-yB, -yB], color=c, zorder=z, alpha=0.5, ec='none')
    ax.fill_between([-xB,xDom+xB], [yDom, yDom],[yDom+yB, yDom+yB], color=c, label=l, zorder=z, alpha=0.5, ec='none')
    ax.fill_betweenx([yMin, yDom], [-xB, -xB],[xMin, xMin], color=c, zorder=z, alpha=0.5, ec='none')
    ax.fill_betweenx([yMin, yDom], [xDom+xB, xDom+xB],[xDom, xDom], color=c, zorder=z, alpha=0.5, ec='none')


def visualizeCoordinates(r, r0, d):
    x, y, z = r
    x0, y0, z0 = r0
    fig, axs = plt.subplots(2, 1)
    axs[0].scatter([y0], [z0], s=4, c='black')
    axs[0].scatter([y], [z], s=4, c='blue')
    axs[0].plot([0,y], [0,z], zorder=0, c='blue', alpha=0.5, label='$r_0$')
    axs[0].plot([0,y0], [0,z0], zorder=0, c='black', alpha=0.5, label='$r$')
    axs[0].plot([y0,y], [z0,z], zorder=0, c='red', alpha=0.5, label='$|r-r_0|$')
    axs[0].set_xlim((0-20, d[1]+20))
    axs[0].set_ylim((0-20, d[2]+20))
    axs[0].set_ylabel("z-axis")
    axs[0].set_xticks([])
    drawBound(axs[0], d[1], d[2], 0, 0, 20, 20, 'black', 'PML', -3)
    drawBound(axs[0], d[1], d[2], 0, 0, -10, -10, 'red', 'SF', -2)
    axs[1].scatter([y0], [x0], s=4, c='black')
    axs[1].scatter([y], [x], s=4, c='blue')
    axs[1].plot([0,y], [0,x], zorder=0, c='blue', alpha=0.5, label='$r_0$')
    axs[1].plot([0,y0], [0,x0], zorder=0, c='black', alpha=0.5, label='$r$')
    axs[1].plot([y0,y], [x0,x], zorder=0, c='red', alpha=0.5, label='$|r-r_0|$')
    axs[1].set_xlim((0-20, d[1]+20))
    axs[1].set_ylim((0-20, d[0]+20))
    axs[1].set_ylabel("x-axis")
    axs[1].set_xlabel("y-axis")
    drawBound(axs[1], d[1], d[0], 0, 0, 20, 20, 'black', '', -3)
    drawBound(axs[1], d[1], d[0], 0, 0, -10, -10, 'red', '', -2)

    axs[0].legend(loc='center', ncols=5, bbox_to_anchor=(0.5, -0.1))
    plt.tight_layout()
    plt.savefig("PositionDiagram.png", dpi =200)

    
    


if __name__=="__main__":
    print("Dyadic Green's Function")


    domain = [300, 600, 300]
    center = [int(domain[0]/2),int(domain[1]/2),int(domain[2]/2)]

    
    x0, y0, z0 = center
    x, y, z = [x0, domain[1]-5, z0]
    
    R0 = [x0,y0,z0]
    R = [x,y,z]

    visualizeCoordinates(R, R0, domain)




    #scalar_greens_function(1,[0,0,0],[0,0,0])