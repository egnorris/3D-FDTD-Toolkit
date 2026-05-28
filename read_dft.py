import os
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import read_simulation_parameters as ini


def OpenCEV(filename, plane="XYZ", dtype="float64", ghost=False, vector=True):
    # need to open FIRST as a 32 bit integer file to grab shape
    frameShape = list(np.fromfile(filename, dtype=np.int32, count=3))
    
    # some files contain "ghost cell"
    if ghost:
        frameShape = [i + 1 for i in frameShape]

    # some files have 3 components for each value
    if vector:
        frameShape.append(3)

    # adjust frameshape based off plane information:
    if plane is None or plane.upper() == "XYZ":
        pass
    elif plane.upper() == "XY":
        frameShape.pop(2)
    elif plane.upper() == "XZ":
        frameShape.pop(1)
    elif plane.upper() == "YZ":
        frameShape.pop(0)
    else:
        raise RuntimeError(f"Plane input not recognized: '{plane}'")
    
    return np.fromfile(filename, dtype=dtype, offset=12).reshape(*frameShape)

def load_dft_data(fn, p):
    dat = OpenCEV(fn, plane=p, dtype="complex128", ghost=False, vector=True)
    x_dat = dat[:,:,0]
    y_dat = dat[:,:,1]
    z_dat = dat[:,:,2]
    mag_dat = np.sqrt(np.sum(dat**2, axis=2))
    return x_dat, y_dat, z_dat, mag_dat

def plot_frame(dat, fname, vmin=0, vmax=1, l=10, w=10):
    vmax = 5e9
    fig, ax = plt.subplots(1, 1, figsize=(l, w))
    ax.set_xticks([])
    ax.set_yticks([])
    im = ax.imshow(dat, cmap='jet', vmin=vmin, vmax=vmax)
    #plt.colorbar(im)
    plt.tight_layout()
    
    plt.savefig(f"{fname}.png", transparent=True, dpi=300)
    plt.close()


def magnitude(z):
    return np.sqrt(np.real(z)**2 + np.imag(z)**2)

def find_nearest_wavelength(wl, wavelengths):
    wl = min(wavelengths, key=lambda x:abs(x-wl))
    idx = wavelengths.index(wl)
    return wl, idx


def plotFieldMonitor(simDIR, p, wl, yc):
    monitorDict, monitorDF, metadata = ini.read_inidef(simDIR, v=False)
    df = monitorDF.loc[monitorDF['plane'] == p]
    df = df.loc[df['y center'] == yc]
    mask = df['mask'].iloc[0]
    dft_files = ini.collect_dft_files(mask)
    wavelengths = ini.collect_wavelength_list(dft_files)
    wl, idx = find_nearest_wavelength(wl, wavelengths)
    fn = dft_files[idx]
    Ex, Ey, Ez, E = load_dft_data(fn, p)
    fname = fn.split('/')[-1]
    fname = fname.split('.')[0]
    vmax = np.max(magnitude(E))
    if p == 'XZ':
        l = 10
        w = 10
    elif p == "YZ":
        l = 10
        w = 20
    elif p == "XY":
        l = 20
        w = 10
    plot_frame(magnitude(Ex), fname=f"{simDIR}/Analysis/{fname}-{p}-Ex", vmax=vmax,l=l,w=w)
    plot_frame(magnitude(Ey), fname=f"{simDIR}/Analysis/{fname}-{p}-Ey", vmax=vmax,l=l,w=w)
    plot_frame(magnitude(Ez), fname=f"{simDIR}/Analysis/{fname}-{p}-Ez", vmax=vmax,l=l,w=w)
    plot_frame(magnitude(E), fname=f"{simDIR}/Analysis/{fname}-{p}-E", vmax=vmax,l=l,w=w)


def plotYZspectrum(simDIR):
    p = 'YZ'
    yc = 300
    monitorDict, monitorDF, metadata = ini.read_inidef(simDIR, v=False)
    df = monitorDF.loc[monitorDF['plane'] == p]
    df = df.loc[df['y center'] == yc]
    mask = df['mask'].iloc[0]
    dft_files = ini.collect_dft_files(mask)
    wavelengths = ini.collect_wavelength_list(dft_files)
    spec = np.zeros((len(dft_files), 9))
    for k in range(len(dft_files)):
        fn = dft_files[k]
        wl = wavelengths[k]
        Ex, Ey, Ez, E = load_dft_data(fn, p)
        E = magnitude(E)
        Ex = magnitude(Ex); Ey = magnitude(Ey); Ez = magnitude(Ez)
        spec[k, 0] = wl
        spec[k, 1] = Ex[150, 150]; spec[k, 5] = Ex[595, 150]
        spec[k, 2] = Ey[150, 150]; spec[k, 6] = Ey[595, 150]
        spec[k, 3] = Ez[150, 150]; spec[k, 7] = Ez[595, 150]
        spec[k, 4] = E[150, 150]; spec[k, 8] = E[595, 150]
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.scatter(spec[:, 0], spec[:, 1], label="y=150")
    ax.scatter(spec[:, 0], spec[:, 5], label="y=595")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("$|E_x|$")
    ax.set_yscale("log")
    ax.set_ylim((0, np.max(spec[:,1:])))
    ax.legend()
    ax.set_title("$|E_x|$ Spectrum")
    plt.tight_layout()
    plt.savefig(f"{simDIR}/Analysis/Ex-spectrum.png", transparent=False, dpi=300)
    plt.close()

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.scatter(spec[:, 0], spec[:, 2], label="y=150")
    ax.scatter(spec[:, 0], spec[:, 6], label="y=595")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("$|E_y|$")
    ax.set_yscale("log")
    ax.set_ylim((0, np.max(spec[:,1:])))
    ax.legend()
    ax.set_title("$|E_y|$ spectrum")
    plt.tight_layout()
    plt.savefig(f"{simDIR}/Analysis/Ey-spectrum.png", transparent=False, dpi=300)
    plt.close()

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.scatter(spec[:, 0], spec[:, 3], label="y=150")
    ax.scatter(spec[:, 0], spec[:, 7], label="y=595")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("$|E_z|$")
    ax.set_yscale("log")
    ax.set_ylim((0, np.max(spec[:,1:])))
    ax.legend()
    ax.set_title("$|E_z|$ spectrum")
    plt.tight_layout()
    plt.savefig(f"{simDIR}/Analysis/Ez-spectrum.png", transparent=False, dpi=300)
    plt.close()

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.scatter(spec[:, 0], spec[:, 4], label="y=150")
    ax.scatter(spec[:, 0], spec[:, 8], label="y=595")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("$|E|$")
    ax.set_yscale("log")
    ax.set_ylim((0, np.max(spec[:,1:])))
    ax.legend()
    ax.set_title("$|E|$ spectrum")
    plt.tight_layout()
    plt.savefig(f"{simDIR}/Analysis/E-spectrum.png", transparent=False, dpi=300)
    plt.close()




if __name__=="__main__":
    simDIR = os.getcwd()
    try:
        os.mkdir(f"{simDIR}/Analysis/")
    except OSError as e:
        print("Error:", e)
    plotYZspectrum(simDIR)
    plotFieldMonitor(simDIR, 'XZ', 400, 150)
    plotFieldMonitor(simDIR, 'XZ', 800, 150)

    plotFieldMonitor(simDIR, 'XZ', 400, 595)
    plotFieldMonitor(simDIR, 'XZ', 800, 595)

    plotFieldMonitor(simDIR, 'XY', 400, 300)
    plotFieldMonitor(simDIR, 'XY', 800, 300)

    plotFieldMonitor(simDIR, 'YZ', 400, 300)
    plotFieldMonitor(simDIR, 'YZ', 800, 300)



