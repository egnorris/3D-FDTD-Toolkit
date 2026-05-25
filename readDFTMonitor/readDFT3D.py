import argparse
import json
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.io import savemat
import glob

import readDFT

def complex_magntiude(A):
    return(np.sqrt(np.real(A)**2 + np.imag(A)**2))

def frame_plot(E, label):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(E, cmap='jet', vmin=0, vmax=1)
    plt.tight_layout()
    plt.savefig(f"{simDIR}/DFTFrames/{label}.png", transparent=True, dpi=300)
    plt.close()

def extract_wavelength(f):
    f = f.split('_')
    if len(f) == 3:
        wl = f[1]
        return wl

    else:
        wl = f[4]
        wl = wl.split('.')[0]
        return wl


def save_comp_frames(d, y, wl):
    for k in d.keys():
        frame_plot(d[k], f"|{k}|-{y}-{wl}")


def repackage_3D_monitor_cev(simDIR,monitor_index, plotWavelength=None, plotFrames=False, ystep=5):
    try:
        os.mkdir(f"{simDIR}/DFTFrames")
    except OSError as e:
        print("Error:", e)

    if monitor_index == "XY":
        dftMask = f"E_*nm_XY.cev"
        print("Default Montitors are not 3D")
        return None
    elif monitor_index == "YZ":
        dftMask = f"E_*nm_YZ.cev"
        print("Default Montitors are not 3D")
        return None
    elif monitor_index == "XZ":
        dftMask = f"E_*nm_XZ.cev"
        print("Default Montitors are not 3D")
        return None
    else:
        dftMask = f"E_DFT_{monitor_index}_WL*nm.cev"
    
    dftFiles = glob.glob(f"{simDIR}/OUTPUT/DFT/{dftMask}")
    full_monitor_dict = {}
    

    if plotWavelength != None:
        plotWL = []
        available_wavelengths = []

        for f in dftFiles:
            wl = extract_wavelength(f)
            available_wavelengths.append(int(wl.split("nm")[0]))
        
        for wl in plotWavelength:
            w, _ = readDFT.get_nearest_wavelength(int(wl), available_wavelengths)
            plotWL.append(f"{w}nm")

    for f in dftFiles:
        wl = extract_wavelength(f)
        
        E = readDFT.OpenCEV(f, plane="XYZ", dtype="complex128", ghost=False, vector=True)

        temp = {
            "Ex": E[:, :, :, 0],
            "Ey": E[:, :, :, 1],
            "Ez": E[:, :, :, 2],
            "wavelength": wl}

        if plotFrames == True:
            if plotWavelength == None:
                Ex = E[:, :, :, 0]
                Ey = E[:, :, :, 1]
                Ez = E[:, :, :, 2]
                E = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2)
                Ex = complex_magntiude(Ex)
                Ey = complex_magntiude(Ey)
                Ez = complex_magntiude(Ez)
                for y in np.arange(0,np.shape(E)[1], ystep):
                    print(f"y: {y} - wl: {wl}")
                    e_dict = {
                        "Ex": Ex[:,y,:] / np.max(Ex),
                        "Ey": Ey[:,y,:] / np.max(Ey),
                        "Ez": Ez[:,y,:] / np.max(Ez),
                        "E": E[:,y,:] / np.max(E),
                        }
                    save_comp_frames(e_dict, y, wl)
            else:
                if wl in plotWL:
                    Ex = E[:, :, :, 0]
                    Ey = E[:, :, :, 1]
                    Ez = E[:, :, :, 2]
                    E = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2)
                    Ex = complex_magntiude(Ex)
                    Ey = complex_magntiude(Ey)
                    Ez = complex_magntiude(Ez)
                    for y in np.arange(0,np.shape(E)[1], ystep):
                        print(f"y: {y} - wl: {wl}")
                        e_dict = {
                            "Ex": Ex[:,y,:] / np.max(Ex),
                            "Ey": Ey[:,y,:] / np.max(Ey),
                            "Ez": Ez[:,y,:] / np.max(Ez),
                            "E": E[:,y,:] / np.max(E),
                            }
                        save_comp_frames(e_dict, y, wl)

                
                
                

            
        #save individual .mat file
        savemat(f"{f}.mat", temp)
        full_monitor_dict[wl] = temp
    savemat(f"{simDIR}/OUTPUT/DFT/E_DFT_1.mat", full_monitor_dict)
    return None


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Read DFT data")
    parser.add_argument('-simDIR', type=str, required=True)
    parser.add_argument('-wl', '--wavelength', nargs='+', required=False, default=None)
    parser.add_argument('-ystep', type=int, required=False, default=5)
    parsedArgs = parser.parse_args().__dict__
    simDIR = parsedArgs["simDIR"]
    wl = parsedArgs["wavelength"]
    if simDIR == '.':
        simDIR = os.getcwd()
    simDIRsep = simDIR.split('/')
    print("simDIR")
    monitor_information_dict = readDFT.read_monitor_info(simDIR)
    nMonitors = len(monitor_information_dict['dimensions'])
    for n in range(nMonitors):
        if monitor_information_dict['dimensions'][n] == 3:
            print(f"{monitor_information_dict['format'][n]} Monitor {n+1} is 3D")
            repackage_3D_monitor_cev(simDIR, n+1, plotFrames=True, plotWavelength=wl, ystep=parsedArgs['ystep'])
