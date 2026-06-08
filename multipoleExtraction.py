import numpy as np
import json
import matplotlib.pyplot as plt
import os
import scipy.special as sp
from scipy.io import savemat

def Hankel(x,n):
    OUT = np.zeros(len(x),dtype=np.complex128)
    for i in range(len(x)):
        OUT[i] = sp.spherical_jn(n,x[i]) + 1j*sp.spherical_yn(n,x[i])
    return OUT

def open_pphinfoini(simDIR):
    with open(f"{simDIR}/INIDEF/pphinfoini.json", 'r') as file:
        return json.load(file)

def load_simulation_parameters(simDIR, v=False):
    ini = open_pphinfoini(simDIR)
    dx, dy, dz = ini["Space Step"]
    nx, ny, nz = ini["Domain Size"]
    nt = ini["Number of Time Steps"]
    w0 = ini["Minimum Wavelength"]
    w1 = ini["Maximum Wavelength"]
    wn = ini["Number of Wavelengths"]
    dt = 0.5*dy/3E8
    r_pr, n_pr_theta, n_pr_phi = ini["Multipoles"]
    n_probes = n_pr_theta*n_pr_phi
    phi = np.linspace(0,2*np.pi,n_pr_theta)
    theta = np.linspace(0,np.pi,n_pr_theta)
    dphi = phi[1] - phi[0]
    dtheta = theta[1] - theta[0]
    out = {
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "dt": dt,
        "dtheta":dtheta,
        "dphi": dphi,
        "total wavelengths": wn,
        "probe radius": r_pr,
        "theta probes": n_pr_theta,
        "phi probes": n_pr_phi,
        "total probes": n_probes,
        "domain": ini["Domain Size"]
    }
    if v == True:
        print("Multipole Monitor Details")
        print(f"Radius of Multipole Monitor: {r_pr} cells, {int(np.round(r_pr*dx*(1E9)))} nm")
        print(f"{n_pr_theta} Monitors along θ, polar angle from z-axis (0, π)")
        print(f"{n_pr_phi} Monitors along ϕ, azimuthal angle from xy-plane (0, 2π)")
        
        print("FDTD Simulation Details")
        print(f"Simulation Domain: {int(round(nx*dx*1E9))}nm X {int(round(ny*dy*1E9))}nm X {int(round(nz*dz*1E9))}nm")
        print(f"Simulation Time: {round(nt*dt*1E15,2)} Femtoseconds")
        print(f"{nt} {dt:.1e}s Time Steps")
        print(f"{wn} wavelengths between {int(round(w0*1E9))}nm and {int(round(w1*1E9))}nm")
        
    return out



def open_multipole_monitor(fname):
    """
        Read data from multipole monitor 
    """
    monitor_location = np.loadtxt(fname,max_rows=1)
    monitor_field = np.loadtxt(fname,skiprows=1)
    return monitor_location, monitor_field


def get_multipole_field_data(simDIR, params):
    #calculate r.E and r.H for later integration
    NumMultipoles = params['total probes']
    Number_of_wavelengths = params['total wavelengths']
    Ex_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    Ey_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    Ez_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    Hx_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    Hy_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    Hz_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    r_dot_Er_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    r_dot_Hr_arr = np.zeros([Number_of_wavelengths,NumMultipoles],dtype=np.complex128)
    x_arr = np.zeros(NumMultipoles)
    y_arr = np.zeros(NumMultipoles)
    z_arr = np.zeros(NumMultipoles)
    phi = np.zeros(NumMultipoles)
    theta = np.zeros(NumMultipoles)
    radius = []


    for i in range(NumMultipoles):
        fname =f"multipole_monitor/OUTPUTEfield_Tracker_{i}.txt"
        L, A =  open_multipole_monitor(fname)
        _, A0 =  open_multipole_monitor(f"EmptySim/{fname}")
        x = L[0]*params['dx']; y = L[1]*params['dy']; z = L[2]*params['dz']
        
        wl = A[:,0]
        Ex = A[:,1] + 1j*A[:,2] - (A0[:,1] + 1j*A0[:,2])
        Ey = A[:,3] + 1j*A[:,4] - (A0[:,3] + 1j*A0[:,4])
        Ez = A[:,5] + 1j*A[:,6] - (A0[:,5] + 1j*A0[:,6])
        Hx = A[:,7] + 1j*A[:,8] - (A0[:,7] + 1j*A0[:,8])
        Hy = A[:,9] + 1j*A[:,10] - (A0[:,9] + 1j*A0[:,10])
        Hz = A[:,11] + 1j*A[:,12] - (A0[:,11] + 1j*A0[:,12])

        Ex_arr[:,i] = Ex #I guess we dont really need these
        Ey_arr[:,i] = Ey
        Ez_arr[:,i] = Ez
        Hx_arr[:,i] = Hx
        Hy_arr[:,i] = Hy
        Hz_arr[:,i] = Hz

        r_dot_Er_arr[:,i] = (x*Ex + y*Ey + z*Ez)
        r_dot_Hr_arr[:,i] = (x*Hx + y*Hy + z*Hz)
        phi[i] = np.arctan2(y,x)
        theta[i] = np.arccos(z/(np.sqrt(x*x+y*y+z*z)))
        radius.append(np.sqrt(x*x+y*y+z*z))
    phi[phi<0] += 2*np.pi

    out = {
        "radius": radius,
        "theta": theta,
        "phi": phi,
        "wavelengths": wl,
        "Ex": Ex_arr,
        "Ey": Ey_arr,
        "Ez": Ez_arr,
        "Hx": Hx_arr,
        "Hy": Hy_arr,
        "Hz": Hz_arr,
        "r.E": r_dot_Er_arr,
        "r.H": r_dot_Hr_arr
        }
    return out


def plot_probe_positions(simDIR, params):
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel("x-axis")
    ax.set_ylabel("y-axis")
    ax.set_zlabel("z-axis")
    X,Y,Z = params["domain"]
    ax.set_xlim((0,X))
    ax.set_ylim((0,Y))
    ax.set_zlim((0,Z))
    ax.scatter([X/2], [Y/2], [Z/2], s = 1, c='red')
    ax.set_title("Multipole Probe Positions")
    for i in range(params['total probes']):
        fname =f"multipole_monitor/OUTPUTEfield_Tracker_{i}.txt"
        L, _ =  open_multipole_monitor(fname)
        x,y,z = L
        ax.scatter([x+(X/2)], [y+(Y/2)], [z+(Z/2)], s=1, c='black')
        
    plt.tight_layout()
    plt.savefig("multipole-probe-positions.png", dpi=300)


def extract_multipole(field_data, params, l=1, m=1):
    Z0 = 376.73
    NumProbes = params['total probes']
    elec_mult_int = 0
    mag_mult_int = 0
    check = 0
    radius = field_data['radius']
    theta = field_data['theta']
    phi = field_data['phi']
    dtheta = params['dtheta']
    dphi = params['dphi']
    wl = field_data['wavelengths']
    for i in range(NumProbes):
        r_dot_Er = field_data['r.E'][:,i]
        r_dot_Hr = field_data['r.H'][:,i]
        Y = sp.sph_harm_y(l,m,theta[i],phi[i])
        elec_mult_int += np.conjugate(Y)*r_dot_Er*np.sin(theta[i])*dphi*dtheta #Eq. 9.123 of Jackson
        mag_mult_int  += np.conjugate(Y)*r_dot_Hr*np.sin(theta[i])*dphi*dtheta #Eq. 9.123 of Jackson
        check += np.conjugate(Y)*Y*np.sin(theta[i])*dphi*dtheta #This should add up to 1
    radius = np.array(radius)
    mean_radius = np.mean(radius)
    wavenumber = np.pi*2.0/wl

    elec_mult_int = -elec_mult_int * wavenumber/np.sqrt(l*(l+1))
    mag_mult_int = mag_mult_int * wavenumber/np.sqrt(l*(l+1))

    elec_mult_int = elec_mult_int / (Z0*Hankel(wavenumber*mean_radius,l))
    mag_mult_int = mag_mult_int / (Hankel(wavenumber*mean_radius,l))

    aE = np.zeros((len(elec_mult_int), 3))
    aM = np.zeros((len(mag_mult_int), 3))

    aE[:,0] = wl; aM[:,0] = wl
    aE[:,1] = np.real(elec_mult_int)
    aE[:,2] = np.imag(elec_mult_int)

    aM[:,1] = np.real(mag_mult_int)
    aM[:,2] = np.imag(mag_mult_int)

    return aE, aM








if __name__=="__main__":
    simDIR = os.getcwd()
    params = load_simulation_parameters(simDIR, v=False)
    plot_probe_positions(simDIR, params)
    fields = get_multipole_field_data(simDIR, params)
    extracted_multipoles = {}
    for l in range(1, 3):
        for m in range(-l,l+1):
            print(f"Multipole: {l},{m}")
            aE, aM = extract_multipole(fields, params, l=1, m=1)
            electric_multipole = {"real": aE[:,1], "imag": aE[:,2]}
            magnetic_multipole = {"real": aM[:,1], "imag": aM[:,2]}
            extracted_multipoles[f"wl"] = aE[:,0]
            extracted_multipoles[f"aE{l}{m}"] = electric_multipole
            extracted_multipoles[f"aM{l}{m}"] = magnetic_multipole

    
    savemat("MutipoleFieldMonitor.mat", fields)
    savemat("MultipoleCoefficients.mat", extracted_multipoles)