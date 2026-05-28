import pandas as pd
import os
from glob import glob
import json
import numpy as np

def get_monitor_filename_mask(simDIR, format=None, plane=None, custom_monitor_index=None):
    if format == 'default':
        return f"{simDIR}/OUTPUT/DFT/E_*nm_{plane}.cev"
    elif format == 'custom':
        return f"{simDIR}/OUTPUT/DFT/E_DFT_{custom_monitor_index}_WL_*nm.cev"

def get_monitor_plane(monitor_span):
    temp = [i for i, x in enumerate(monitor_span) if x != 1]
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
    return plane


def load_json(fname):
    with open(fname, 'r') as file:
        return json.load(file)

def load_txt(fname):
    with open(fname, 'r') as file:
        lines = []
        temp = file.readlines()
        for l in temp:
            lines.append(l.split('\n')[0])
        return lines

def read_key(k, d, keys):
    if k in keys:
        return d[k]
    else:
        return 'undefined'

def read_inidef(simDIR, v=False):
    c0 = 299792458
    metadata = {}

    #get a list of json files
    json_file_list = glob(f"{simDIR}/INIDEF/*.json")
    txt_file_list = glob(f"{simDIR}/INIDEF/*.txt")

    metadata["custom geometry"] = 0
    metadata["custom monitors"] = 0
    metadata["material ini"] = 0
    metadata["nls ini"] = 0

    monitor_sx = []
    monitor_sy = []
    monitor_sz = []
    monitor_cx = []
    monitor_cy = []
    monitor_cz = []
    monitor_plane = []
    monitor_mask = []
    monitor_type = []
    if f"{simDIR}/INIDEF/geometry.json" in json_file_list:
        temp = load_json(f"{simDIR}/INIDEF/geometry.json")
        if len(temp) > 0:
            metadata["custom geometry"] = 1
            metadata["custom geometry entries"] = len(temp)

    if f"{simDIR}/INIDEF/monitors.json" in json_file_list:
        temp = load_json(f"{simDIR}/INIDEF/monitors.json")
        if len(temp['Monitors']) > 0:
            metadata["custom monitors"] = 1
            metadata["custom monitors"] = len(temp['Monitors'])
        for k in range(len(temp['Monitors'])):
            sx, sy, sz = temp['Monitors'][k]['Size']
            cx, cy, cz = temp['Monitors'][k]['Center']
            t = temp['Monitors'][k]['Type']
            p = get_monitor_plane([sx, sy, sz])
            m = get_monitor_filename_mask(simDIR,'custom', p,k+1)
            monitor_sx.append(sx);monitor_sy.append(sy);monitor_sz.append(sz)
            monitor_cx.append(cx);monitor_cy.append(cy);monitor_cz.append(cz)
            monitor_plane.append(p);monitor_mask.append(m);monitor_type.append(t)

    
    if f"{simDIR}/INIDEF/pphmatini.txt" in txt_file_list:
        mat = load_txt(f"{simDIR}/INIDEF/pphmatini.txt")
        if len(mat) > 0:
            metadata["material ini"] = 1
            for k in range(len(mat)):
                metadata[f"material {k+1} index"] = mat[k]

    #pphnlsini

    temp = load_json(f"{simDIR}/INIDEF/pphinfoini.json")
    keys = temp.keys()
    xs, ys, zs = temp['Domain Size']
    xc, yc, zc = temp['Center Position']
    metadata['dx'], metadata['dy'], metadata['dz'] = temp['Space Step']

    metadata['center x cell']=xc;metadata['x domain']=xs
    metadata['center y cell']=yc;metadata['y domain']=ys
    metadata['center z cell']=zc;metadata['z domain']=zs
    metadata['dt'] = np.min(temp['Space Step'])/(2*c0)
    metadata['nT'] = temp['Number of Time Steps']
    am = read_key('Advanced Model', temp, keys)
    if am == 3:
        metadata['hydrodynamic'] = 'Full'
    elif am == 4:
        metadata['hydrodynamic'] = 'No Pressure Term'
    else:
        metadata['hydrodynamic'] = 'False'

    metadata['polarization'] = read_key('Polarization Angle', temp, keys)
    metadata['signal'] = read_key('Signal Type', temp, keys)
    metadata['pulse width'] = read_key('Pulse Width', temp, keys)
    metadata['maximum field'] = read_key('Maximum Field', temp, keys)
    
    if read_key('First Medium', temp, keys) != 'undefined':
        n = read_key('First Medium', temp, keys)
        metadata['first medium index'] = metadata[f"material {n} index"]
    if read_key('Middle Medium', temp, keys) != 'undefined':
        n = read_key('Middle Medium', temp, keys)
        metadata['middle medium index'] = metadata[f"material {n} index"]
    if read_key('Last Medium', temp, keys) != 'undefined':
        n = read_key('Last Medium', temp, keys)
        metadata['last medium index'] = metadata[f"material {n} index"]
    if read_key('Antenna Medium', temp, keys) != 'undefined':
        n = read_key('Antenna Medium', temp, keys)
        metadata['antenna medium index'] = metadata[f"material {n} index"]

    d = read_key('DFT Plot', temp, keys)
    if d == 1:
        p = ['XY']
        sx=[xs,];sy=[ys,];sz=[1,]
    elif d == 2:
        p = ['XZ']
        sx=[xs,];sy=[ys,];sz=[1,]
    elif d == 3:
        p = ['YZ']
        sx=[1,];sy=[ys,];sz=[zs,]
    elif d == 4:
        p = ['XY', 'XZ', 'YZ']
        sx=[xs,xs,1];sy=[ys,1,ys];sz=[1,zs,zs]
    else:
        p = []

    for k in range(len(p)):
        m = get_monitor_filename_mask(simDIR,'default', p[k])
        monitor_sx.append(sx[k]);monitor_sy.append(sy[k]);monitor_sz.append(sz[k])
        monitor_cx.append(xc);monitor_cy.append(yc);monitor_cz.append(zc)
        monitor_plane.append(p[k]);monitor_mask.append(m);monitor_type.append('frequency')

    monitorDict = {
        "x span": monitor_sx,
        "y span": monitor_sy,
        "z span": monitor_sz,
        "x center": monitor_cx,
        "y center": monitor_cy,
        "z center": monitor_cz,
        "plane": monitor_plane,
        "mask": monitor_mask,
        "type": monitor_type}

    monitorDF = pd.DataFrame(monitorDict)

    dft_files = collect_dft_files(monitorDict['mask'][0])
    wavelength_list = np.sort(collect_wavelength_list(dft_files))

    if v==True:
        print("\nSimulation Metadata")
        for key in metadata.keys():
            print(f"{key}: {metadata[key]}")

        print(f"\nAvailable Wavelengths: \n{wavelength_list}")

        print("\nMonitor Information")
        print(monitorDF)

    metadata['available wavelengths'] = wavelength_list
    return monitorDict, monitorDF, metadata

def extract_wavelength(f):
    f = f.split('_')
    if len(f) == 3:
        wl = f[1]
        wl = wl.split('nm')[0]
        return wl

    else:
        wl = f[4]
        wl = wl.split('.')[0]
        wl = wl.split('nm')[0]
        return wl

def collect_dft_files(mask):
    return glob(f"{mask}")

def collect_wavelength_list(dft_files):
    w = []
    for f in dft_files:
        w.append(int(extract_wavelength(f)))
    return w





if __name__=="__main__":
    simDIR = os.getcwd()

    monitorDict, monitorDF, metadata = read_inidef(simDIR, v=True)
