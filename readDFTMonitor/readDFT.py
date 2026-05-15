import argparse
import json

def read_monitor_info(simDIR):
    """
        read simDIR/INIDEF/monitors.json and 
        simDIR/INIDEF/pphinfoini.json to find
        information about both custom monitors
        defined in monitors.json and the built
        in DFT monitors from pphinfoini.json
    """
    monitiors_fname = f"{simDIR}/INIDEF/monitors.json"
    ini_fname = f"{simDIR}/INIDEF/pphinfoini.json"


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