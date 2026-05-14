import numpy as np
import matplotlib.pyplot as plt



def drawBound(ax, xDom, yDom, xMin=0, yMin=0, xB=20, yB=20, c='red', l='', z=-2):
    #ax.fill([-xB, xDom+xB, xDom+xB, -xB], [-yB, -yB, yDom+yB, yDom+yB], color=c, zorder=z, label=l)
    ax.fill_between([-xB,xDom+xB], [yMin, yMin],[-yB, -yB], color=c, zorder=z, alpha=0.5, ec='none')
    ax.fill_between([-xB,xDom+xB], [yDom, yDom],[yDom+yB, yDom+yB], color=c, label=l, zorder=z, alpha=0.5, ec='none')
    ax.fill_betweenx([yMin, yDom], [-xB, -xB],[xMin, xMin], color=c, zorder=z, alpha=0.5, ec='none')
    ax.fill_betweenx([yMin, yDom], [xDom+xB, xDom+xB],[xDom, xDom], color=c, zorder=z, alpha=0.5, ec='none')


def visualize_coordinates(r, r0, d):
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


def scalar_greens_function(wavelength,R):
    k = 2*np.pi/wavelength
    G0 = np.exp(1j*k*R)/(4*np.pi*R)
    return G0

def dyadic_greens_function(wavelength, r, r0, verbose=False):
    r_diff = np.asarray(r) - np.asarray(r0)
    R = np.linalg.norm(np.abs(r_diff))
    RR = np.outer(r_diff, r_diff)
    k = 2*np.pi/wavelength
    if verbose == True:
        print(f"\nr0:             ({r0[0]}nm, {r0[1]}nm, {r0[2]}nm)")
        print(f"r:              ({r[0]}nm, {r[1]}nm, {r[2]}nm) ")
        print(f"r-r0:           ({r_diff[0]}nm ,{r_diff[1]}nm, {r_diff[2]}nm)")
        print(f"||r-r0||:       {R}nm ")
        print(f"||r-r0||^2:     {R**2:.2e} nm^2 ")
        print(f"                |{RR[0,0]:.2e} nm^2, {RR[0,1]:.2e} nm^2, {RR[0,2]:.2e} nm^2|")
        print(f"RR:             |{RR[1,0]:.2e} nm^2, {RR[1,1]:.2e} nm^2, {RR[1,2]:.2e} nm^2|")
        print(f"                |{RR[2,0]:.2e} nm^2, {RR[2,1]:.2e} nm^2, {RR[2,2]:.2e} nm^2|")
        print(f"\nwavelength:     {wavelength}nm")
        print(f"wavenumber:     {k:.2e} nm^-1")
    G0 = scalar_greens_function(wavelength,R)
    kR = k*R
    k2R2 = kR*kR
    ikR = 1j*kR
    a = np.exp(ikR)/(4*np.pi*R)
    b = 1 + (ikR-1)/(k2R2)
    c = (3-3*ikR-k2R2)/(k2R2)
    I = np.array([[1,0,0],[0,1,0],[0,0,1]])
    G = a*(b*I + c*RR)
    if verbose == True:
        print(f"\nG0:             ({G0:.2e}) nm^-1\n")
        print(f"                |({G[0,0]:.2e}) nm^-1, ({G[0,1]:.2e}) nm^-1, ({G[0,2]:.2e}) nm^-1|")
        print(f"G:              |({G[1,0]:.2e}) nm^-1, ({G[1,1]:.2e}) nm^-1, ({G[1,2]:.2e}) nm^-1|")
        print(f"                |({G[2,0]:.2e}) nm^-1, ({G[2,1]:.2e}) nm^-1, ({G[2,2]:.2e}) nm^-1|")
    
    return G



if __name__=="__main__":
    print("Dyadic Green's Function")


    domain = [300, 600, 300]
    center = [int(domain[0]/2),int(domain[1]/2),int(domain[2]/2)]

    
    x0, y0, z0 = center
    x, y, z = [x0, domain[1]-5, z0]
    
    R0 = [x0,y0,z0]
    R = [x,y,z]

    visualize_coordinates(R, R0, domain)
    dyadic_greens_function(800, R, R0, verbose=True)