import argparse
import json
import numpy as np

def read_monitor_info(simDIR):
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
    if ini_data["DFT Plot"] == 0:
        num_default_monitors = 0
    elif ini_data["DFT Plot"] == 4:
        num_default_monitors = 3
    else:
        num_default_monitors = 1
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
            monitor_size_list.append(ini_data["Center Position"])
            monitor_center_list.append(ini_data["Center Position"])
            monitor_type_list.append("frequency")
            monitor_plane_list.append(planes[n])
            monitor_dim_list.append(2)
            monitor_format_list.append("Default")
    elif num_default_monitors == 1:
        monitor_size_list.append(ini_data["Center Position"])
        monitor_center_list.append(ini_data["Center Position"])
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

    if len(parsedArgs["wavelength"]) == 1:
        print(f"Reading DFT data from {parsedArgs["simDIR"]} with wavelength: \n    {parsedArgs["wavelength"][0]}nm")
    else:
        print(f"Reading DFT data from {parsedArgs["simDIR"]} with wavelengths:")
        for i in range(len(parsedArgs["wavelength"])):
            print(f"    {parsedArgs["wavelength"][i]}nm")

    simDIR = parsedArgs["simDIR"]
    read_monitor_info(simDIR)