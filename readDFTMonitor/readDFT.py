import argparse
import json
import numpy as np

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
    with open(f"{simDIR}/INIDEF/monitors.json", 'r') as file:
        mon_data = json.load(file)
    
   
    default_monitor_center = ini_data["Center Position"]
    default_monitor_size = ini_data["Domain Size"]
    # Find the total number of available monitors
    num_custom_monitors = len(mon_data["Monitors"])
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
            print(f"    centered at ({c[0]}nm, {c[1]}nm, {c[2]}nm")
            print(f"    spans {s[0]}nm along x-axis")
            print(f"    spans {s[1]}nm along y-axis")
            print(f"    spans {s[2]}nm along z-axis")
        print("========================================================================================================\n")
        
    return monitor_information_dict
    




def get_dft_file(simDIR, wavelength):
    """
        find all of the files in simDIR/OUTPUT/DFT 
        that match the provided wavelength and return
        the filename and coordinate information
    """
    


def read_dft(simDIR, fname):
    """
        read DFT data from simDIR/OUTPUT/DFT/fname
    """
    print(f"Reading DFT file: simDIR/OUTPUT/DFT/{fname}")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Read DFT data")
    parser.add_argument('-simDIR', type=str, required=True)
    parser.add_argument('-wl', '--wavelength', nargs='+', required=True)
    parsedArgs = parser.parse_args().__dict__
    simDIR = parsedArgs["simDIR"]
    wl = parsedArgs["wavelength"]

    if len(wl) == 1:
        print(f"Reading DFT data from {simDIR} with wavelength: \n    {wl[0]}nm")
    else:
        print(f"Reading DFT data from {simDIR} with wavelengths:")
        for i in range(len(wl)):
            print(f"    {wl[i]}nm")

    simDIR = parsedArgs["simDIR"]
    read_monitor_info(simDIR, v=True)
