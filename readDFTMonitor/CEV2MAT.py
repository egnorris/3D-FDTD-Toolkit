import argparse
import json
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.io import savemat
import glob
import readDFT


def collect_monitor_file_list(simDIR,monitor_information, idx):
    p = monitor_information['plane'][idx]
    f = monitor_information['format'][idx]
    i = monitor_information['index'][idx]
    if f == 'Default':
        return glob.glob(f"{simDIR}/OUTPUT/DFT/E_*nm_{p}.cev")
    elif f == 'Custom':
        return glob.glob(f"{simDIR}/OUTPUT/DFT/E_DFT_{i}_WL_*nm.cev")


def collect_wavelength_list(monitor_file_list):
    w = []
    for f in monitor_file_list:
        w.append(int(readDFT.extract_wavelength(f)))
    return w

def repack_CEV2MAT(simDIR,monitor_information, idx):
    p = monitor_information['plane'][idx]
    c = monitor_information['center'][idx]
    s = monitor_information['size'][idx]
    d = monitor_information['dimensions'][idx]
    file_list = collect_monitor_file_list(simDIR,monitor_information, idx)
    
    wavelength_list = collect_wavelength_list(file_list)
    out = {}
    for k in range(len(file_list)):
        fn = file_list[k]
        wl = wavelength_list[k]
        E = readDFT.OpenCEV(fn, plane=p, dtype='complex128', ghost=False, vector=True)
        if d == 1:
            Ex=E[:,0];Ey=E[:,1];Ez=E[:,2]
        if d == 2:
            Ex=E[:,:,0];Ey=E[:,:,1];Ez=E[:,:,2]
        if d == 3:
            Ex=E[:,:,:,0];Ey=E[:,:,:,1];Ez=E[:,:,:,2]
        temp = {
            "Ex": Ex.transpose(),
            "Ey": Ey.transpose(),
            "Ez": Ez.transpose(),
            "wavelength": wl,
            "plane": p,
            "center": c,
            "size": s
            }
        out[f"{wl}nm"] = temp

    output_name = file_list[0]
    output_name = output_name.split("/")[-1]
    if monitor_information['format'][idx] == "Custom":
        output_name = output_name.split("WL")[0]
        output_name = output_name.split("_")[2]
        output_name = f"{simDIR}/OUTPUT/DFT/E_DFT_{output_name}.mat"
    else:
        output_name = output_name.split(".")[0]
        output_name = output_name.split("_")[2]
        output_name = f"{simDIR}/OUTPUT/DFT/E_DFT_{output_name}.mat"
    savemat(output_name, out)
    






if __name__=="__main__":
    simDIR = os.getcwd()
    monitor_information_dict = readDFT.read_monitor_info(simDIR, v=False)
    for k in range(len(monitor_information_dict['format'])):
        repack_CEV2MAT(simDIR, monitor_information_dict, k)


