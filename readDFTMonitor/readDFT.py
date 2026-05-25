import argparse
import json
import numpy as np
import os
import matplotlib.pyplot as plt

def read_monitor_info(simDIR, v=False):
    """
        read simDIR/INIDEF/monitors.json and 
        simDIR/INIDEF/pphinfoini.json to find
        information about both custom monitors
        defined in monitors.json and the built
        in DFT monitors from pphinfoini.json
    """
    #monitiors_fname = f"{simDIR}/INIDEF/monitors.json"
    #ini_fname = f"{simDIR}/INIDEF/pphinfoini.json"
    with open(f"{simDIR}/INIDEF/pphinfoini.json", 'r') as file:
        ini_data = json.load(file)
    try:
        with open(f"{simDIR}/INIDEF/monitors.json", 'r') as file:
            mon_data = json.load(file)
            num_custom_monitors = len(mon_data["Monitors"])
    except FileNotFoundError:
        num_custom_monitors = 0

    
   
    default_monitor_center = ini_data["Center Position"]
    default_monitor_size = ini_data["Domain Size"]
    # Find the total number of available monitors
    
    if "DFT Plot" in ini_data:
        if ini_data["DFT Plot"] == 0:
            num_default_monitors = 0
        elif ini_data["DFT Plot"] == 4:
            num_default_monitors = 3
        else:
            num_default_monitors = 1
    else:
        num_default_monitors = 0
    monitor_size_list = []
    monitor_center_list = []
    monitor_type_list = []
    monitor_plane_list = []
    monitor_dim_list = []
    monitor_format_list = []
    for n in range(num_custom_monitors):
        size = mon_data["Monitors"][n]["Size"]
        monitor_size_list.append(size)
        monitor_center_list.append(mon_data["Monitors"][n]["Center"])
        monitor_type_list.append(mon_data["Monitors"][n]["Type"])
        temp = [i for i, x in enumerate(size) if x != 1]
        plane = ''
        for i in range(len(temp)):
            if temp[i] == 0:
                plane += "X"
            elif temp[i] == 1:
                plane += "Y"
            elif temp[i] == 2:
                plane += "Z"
        if plane == '':
            plane += '0'
        monitor_plane_list.append(plane)
        monitor_dim_list.append(len(temp))
        monitor_format_list.append("Custom")
    planes = ['XY', "XZ", "YZ"]
    if num_default_monitors > 1:
        planes = ['XY', "XZ", "YZ"]
        for n in range(num_default_monitors):
            x,y,z = default_monitor_size
            if planes[n] == 'XY':
                monitor_size_list.append([x, y, 1])
            if planes[n] == 'XZ':
                monitor_size_list.append([x, 1, z])
            elif planes[n] == 'YZ':
                monitor_size_list.append([1, y, z])
            monitor_center_list.append(default_monitor_center)
            monitor_type_list.append("frequency")
            monitor_plane_list.append(planes[n])
            monitor_dim_list.append(2)
            monitor_format_list.append("Default")
    elif num_default_monitors == 1:
        x,y,z = default_monitor_size
        p = planes[ini_data["DFT Plot"]-1]
        if p == 'XY':
            monitor_size_list.append([x, y, 1])
        if p == 'XZ':
            monitor_size_list.append([x, 1, z])
        elif p == 'YZ':
            monitor_size_list.append([1, y, z])
        monitor_center_list.append(default_monitor_center)
        monitor_type_list.append("frequency")
        monitor_plane_list.append(planes[ini_data["DFT Plot"]-1])
        monitor_format_list.append("Default")
        monitor_dim_list.append(2)
    monitor_information_dict = {
        "size": monitor_size_list,
        "center": monitor_center_list,
        "type": monitor_type_list,
        "plane": monitor_plane_list,
        "dimensions": monitor_dim_list,
        "format": monitor_format_list}

    if v == True:
        print("\n========================================================================================================")
        print("Reading INIDEF/monitors.json and INIDEF/pphinfoini.json")
        print("========================================================================================================")
        print(f"There are {num_custom_monitors} custom monitors and {num_default_monitors} default monitors Available")
        for k in range(len(monitor_information_dict["format"])):
            f = monitor_information_dict["format"][k-1]
            c = monitor_information_dict["center"][k-1]
            s = monitor_information_dict["size"][k-1]
            p = monitor_information_dict["plane"][k-1]
            d = monitor_information_dict["dimensions"][k-1]
            print(f"There is a {d}D {f} Custom Monitor in the {p}-plane")
            print(f"    centered at ({c[0]}nm, {c[1]}nm, {c[2]}nm)")
            print(f"    spans {s[0]}nm along x-axis")
            print(f"    spans {s[1]}nm along y-axis")
            print(f"    spans {s[2]}nm along z-axis")

        
    return monitor_information_dict
    
def get_available_wavelengths(simDIR):
    DFTfiles = os.listdir(f"{simDIR}/OUTPUT/DFT")
    available_wavelength_list = []
    for fn in DFTfiles:
        fn = fn.split('nm')
        fn = fn[0]
        fn = fn.split('_')
        if fn[-1] != "Mask.cev" and fn[-1] != "phase.txt" and fn[-1] != "phase.txt":
            available_wavelength_list.append(int(fn[-1]))
    available_wavelength_list.sort()
    #remove duplicate wavelength values
    available_wavelength_list = list(dict.fromkeys(available_wavelength_list))
    return available_wavelength_list

def get_nearest_wavelength(wl, available_wavelength_list):
    wl = min(available_wavelength_list, key=lambda x:abs(x-wl))
    idx = available_wavelength_list.index(wl)
    return (wl, idx)


def get_dft_file(simDIR, wavelengths, monitor_index=None, v=False):
    """
        find all of the files in simDIR/OUTPUT/DFT 
        that match the provided wavelength and return
        the filename and coordinate information
    """
    available_wavelength_list = get_available_wavelengths(simDIR)
    monitor_information_dict = read_monitor_info(simDIR, v)
    
    
    for k in range(len(wavelengths)):
        w, idx = get_nearest_wavelength(int(wavelengths[k]), available_wavelength_list)
        wavelengths[k] = w


    dft_file_list = []
    
    for wl in wavelengths:
        if monitor_index == None:
            custom_monitor_index = 1
            for k in range(len(monitor_information_dict["format"])):
                f = monitor_information_dict["format"][k]
                p = monitor_information_dict["plane"][k]
                if f == "Custom":
                    fname = f"{simDIR}/OUTPUT/DFT/E_DFT_{custom_monitor_index}_WL_{wl}nm.cev"
                    custom_monitor_index += 1
                elif f == "Default":
                    fname = f"{simDIR}/OUTPUT/DFT/E_{wl}nm_{p}.cev"
                dft_dict = {
                    "size": monitor_information_dict['size'][k],
                    "center": monitor_information_dict['center'][k],
                    "type": monitor_information_dict['type'][k],
                    "plane": monitor_information_dict['plane'][k],
                    "dimensions": monitor_information_dict['dimensions'][k],
                    "format": monitor_information_dict['format'][k],
                    "path": fname,
                    "wavelength": wl}
                dft_file_list.append(dft_dict)
        else:
            k = monitor_index
            custom_monitor_index = k + 1
            f = monitor_information_dict["format"][k]
            p = monitor_information_dict["plane"][k]
            if f == "Custom":
                fname = f"{simDIR}/OUTPUT/DFT/E_DFT_{custom_monitor_index}_WL_{wl}nm.cev"
                custom_monitor_index += 1
            elif f == "Default":
                fname = f"{simDIR}/OUTPUT/DFT/E_{wl}nm_{p}.cev"
            dft_dict = {
                "size": monitor_information_dict['size'][k],
                "center": monitor_information_dict['center'][k],
                "type": monitor_information_dict['type'][k],
                "plane": monitor_information_dict['plane'][k],
                "dimensions": monitor_information_dict['dimensions'][k],
                "format": monitor_information_dict['format'][k],
                "path": fname,
                "wavelength": wl}
            dft_file_list.append(dft_dict)

        
    


    if v == True:
        print("\n========================================================================================================")
        print("Checking OUTPUT/DFT for valid monitor data at the following wavelengths: ", end='')
        for wl in wavelengths:
            print(f"{wl}nm  ", end='')
        print("\n========================================================================================================")
        for k in range(len(dft_file_list)):
            print(f"{dft_file_list[k]['format']} {dft_file_list[k]['plane']}-plane Monitor found at {dft_file_list[k]['path']}")
            print(f"    Centered at {dft_file_list[k]['center']} with size of {dft_file_list[k]['size']}")


    return dft_file_list
    


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

def read_dft(dft_file_dict, v=False):
    """
        read DFT data from file specified in dft_file_dict['path']
    """
    dft_data = OpenCEV(dft_file_dict['path'], plane=dft_file_dict['plane'], dtype='complex128', ghost=False, vector=True)
    if v == True:
        print("\n========================================================================================================")
        print(f"Reading {dft_file_dict['format']} DFT data from {dft_file_dict['path']}")
        print("========================================================================================================")
        if dft_file_dict['dimensions'] == 1:
            print(f"{dft_file_dict['plane']} Line centered at ({dft_file_dict['center'][0]}nm, {dft_file_dict['center'][1]}nm, {dft_file_dict['center'][2]}nm) with size of ({dft_file_dict['size'][0]}nm, {dft_file_dict['size'][1]}nm, {dft_file_dict['size'][2]}nm)")
        elif dft_file_dict['dimensions'] == 2:
            print(f"{dft_file_dict['plane']} Plane centered at ({dft_file_dict['center'][0]}nm, {dft_file_dict['center'][1]}nm, {dft_file_dict['center'][2]}nm) with size of ({dft_file_dict['size'][0]}nm, {dft_file_dict['size'][1]}nm, {dft_file_dict['size'][2]}nm)")
        elif dft_file_dict['dimensions'] == 3:
            print(f"{dft_file_dict['plane']} Cube centered at ({dft_file_dict['center'][0]}nm, {dft_file_dict['center'][1]}nm, {dft_file_dict['center'][2]}nm) with size of ({dft_file_dict['size'][0]}nm, {dft_file_dict['size'][1]}nm, {dft_file_dict['size'][2]}nm)")
        elif dft_file_dict['dimensions'] == 0:
            print(f"Point at ({dft_file_dict['center'][0]}nm, {dft_file_dict['center'][1]}nm, {dft_file_dict['center'][2]}nm)")

    return dft_data[:, :, 0].transpose(), dft_data[:, :, 1].transpose(), dft_data[:, :, 2].transpose()



def magnitude(z):
    return np.real(np.sqrt(np.real(z)**2 + np.imag(z)**2))

def plot_dft_comp(ax, dft_file_dict, comp=None, vmin=None, vmax=None):
    Ex, Ey, Ez = read_dft(dft_file_dict)
    E = np.real(np.abs(Ex**2 + Ey**2 + Ez**2))
    p = dft_file_dict['plane']
    dim = dft_file_dict['dimensions']
    if comp == 'x':
        E = magnitude(Ex)
        ax.set_title("$|E_x|$")
        ax.set_xlabel(f"{p[0]}-axis")
        ax.set_ylabel(f"{p[1]}-axis")
    elif comp == 'y':
        ax.set_yticks([])
        E = magnitude(Ey)
        ax.set_title("$|E_y|$")
        ax.set_xlabel(f"{p[0]}-axis")
    elif comp == 'z':
        E = magnitude(Ez)
        ax.set_yticks([])
        ax.set_title("$|E_z|$")
        ax.set_xlabel(f"{p[0]}-axis")
    else:
        E = np.real(np.sqrt(Ex**2 + Ey**2 + Ez**2))
        ax.set_yticks([])
        ax.set_title("$|E|$")
        ax.set_xlabel(f"{p[0]}-axis")


    if vmin == None:
        v0 = 0
    else:
        v0 = vmin
    if vmax == None:
        v1 = np.max(np.real(np.sqrt(Ex**2 + Ey**2 + Ez**2)))
    else:
        v1 = vmax

    if dim == 2:
        cax = ax.imshow(E, cmap='jet', vmin=v0, vmax=v1, origin='lower')
        if comp == "E":
            return cax

def get_dft_spectrum(simDIR, monitor_index=0, x=None, y=None, v=False):
    monitor_information_dict = read_monitor_info(simDIR)
    n_monitors = len(monitor_information_dict['dimensions'])
    available_wavelength_list = get_available_wavelengths(simDIR)
    spectrum = np.zeros((5, len(available_wavelength_list), n_monitors), dtype=np.dtype(np.complex128))
    for n in range(n_monitors):
        dft_file_list = get_dft_file(simDIR, available_wavelength_list, monitor_index=n, v=v)
        for k in range(len(dft_file_list)):
            center = dft_file_list[k]['center']
            plane = dft_file_list[k]['plane']
            if x == None:
                if plane[0] == "X":
                    x = center[0]
                if plane[0] == "Y":
                    x = center[1]
            if y == None:
                if plane[1] == "Y":
                    y = center[1]
                if plane[1] == "Z":
                    y = center[2]
        
            Ex, Ey, Ez = read_dft(dft_file_list[k])
            E = np.real(np.abs(Ex**2 + Ey**2 + Ez**2))
            spectrum[0, k, n] = available_wavelength_list[k]
            spectrum[1, k, n] = Ex[x,y]
            spectrum[2, k, n] = Ey[x,y]
            spectrum[3, k, n] = Ez[x,y]
            spectrum[4, k, n] = E[x,y]
        
    return spectrum




if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Read DFT data")
    parser.add_argument('-simDIR', type=str, required=True)
    parser.add_argument('-wl', '--wavelength', nargs='+', required=True)
    parser.add_argument('-v', '--verbose', type=str, required=False)
    parsedArgs = parser.parse_args().__dict__
    simDIR = parsedArgs["simDIR"]
    v = parsedArgs["verbose"]
    wl = parsedArgs["wavelength"]
    if simDIR == '.':
        simDIR = os.getcwd()
    simDIRsep = simDIR.split('/')
    if v == True:
        print("\n========================================================================================================")
        print(f"Running readDFT.py")
        print("========================================================================================================")
        if len(wl) == 1:
            print(f"Reading DFT data from ../{simDIRsep[-3]}/{simDIRsep[-2]}/{simDIRsep[-1]} with wavelength: \n    {wl[0]}nm")
        else:
            print(f"Reading DFT data from ../{simDIRsep[-3]}/{simDIRsep[-2]}/{simDIRsep[-1]} with wavelengths: ", end='')
            for i in range(len(wl)):
                print(f"{wl[i]}nm   ", end='')
        print('\n')

    #spectrum = get_dft_spectrum(simDIR, monitor_index=0)
    #plt.plot(spectrum[0, :, 0], magnitude(spectrum[4, :, 0]))
    #plt.savefig("temp.png")


    dft_file_list =get_dft_file(simDIR, wl, v)
    os.makedirs(f"{simDIR}/DFTframes", exist_ok=True)
    for k in range(len(dft_file_list)):
        Ex, Ey, Ez = read_dft(dft_file_list[k], v)
        fig, axs = plt.subplots(1,4,figsize=(15, 5), layout='constrained')
        plot_dft_comp(axs[0], dft_file_list[k], comp='x')
        plot_dft_comp(axs[1], dft_file_list[k], comp='y')
        plot_dft_comp(axs[2], dft_file_list[k], comp='z')
        cax = plot_dft_comp(axs[3], dft_file_list[k], comp='E')
        fig.colorbar(cax, ax=axs.ravel().tolist(), orientation='horizontal', fraction=0.15, pad=0.1)
        d = dft_file_list[k]
        wl = d['wavelength']
        p =  d['plane']
        c =  d['center']
        f = d['format']
        plt.suptitle(f"Electric Field {p}-plane at ({c[0]},{c[1]},{c[2]}) - {wl}nm")
        plt.savefig(f'{simDIR}/DFTframes/{f}-DFT_{p}plane_X-{c[0]}_Y-{c[1]}_Z-{c[2]}_{wl}nm.png', dpi=900)
        

    #plt.imshow(np.real(np.abs(Ex**2 + Ey**2 + Ez**2)), cmap='jet', vmin=0)
    #plt.savefig("temp.png")
