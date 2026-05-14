import argparse
import os
import json

def makeSimDirectories(simDIR):
    try:
        os.mkdir(simDIR)
    except OSError as e:
        print("Error:", e)
    try:
        os.mkdir(f'{simDIR}/INIDEF')
    except OSError as e:
        print("Error:", e)


parser = argparse.ArgumentParser(description="setup 3D-FDTD simulation files")
parser.add_argument('-config', type=str, required=False, default='io/mieConfig.json')
parsedArgs = parser.parse_args().__dict__


with open(parsedArgs['config'], 'r') as file:
    data = json.load(file)

print(json.dumps(data, indent=4))
#makeSimDirectories(parsedArgs['simDIR'])
