import os
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser(description="A simple tool to convert csv data to json")
parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
parser.add_argument('-o', '--output', type=str, required=True, help='Output JSON file')
args = parser.parse_args()

assert args.input.endswith(".csv"), "Input file must end with .csv"

output_file = args.output
if os.path.isdir(args.output):
    base = os.path.basename(args.input)
    output_file = os.path.join(args.output, os.path.splitext(base)[0] + '.json')

description = os.path.basename(args.input).upper().split("_")[0]
raw_data = np.loadtxt(args.input,skiprows=1, delimiter=",", usecols=(1,2))

fields = [
    "name", 
    "description", 
    "provenance", 
    "reference", 
    "independent_variable", 
    "independent_variable_units", 
    "independent_variable_label", 
    "limit_units", 
    "limit_label", 
    "confidence level",
    "wimp_mass",
    "exposure",
    "upper_limit",
    "lower_limit",
    "discovery_significance",
    "expected_signal",
    "sensitivity_quantiles",
    "sensitivity_for_quantiles",
]

data = {f:"" for f in fields}
overwrites = dict(
    name = os.path.splitext(os.path.basename(args.input))[0],
    description = description,
    provenance = "collaboration",
    independent_variable = "wimp_mass",
    independent_variable_units = "GeV/c^2",
    independent_variable_label = "WIMP mass [GeV/c$^2$]",
    limit_units = "cm^2",
    limit_label = "WIMP-nucleon cross-section [cm$^2$]",
    confidence_level = "0.9",
    wimp_mass = list(raw_data[:,0]),
    lower_limit = list(np.zeros(len(raw_data[:,0]))),
    upper_limit = list(raw_data[:,1]),
)
data.update(overwrites)
json.dumps(data)
with open(output_file,"w") as json_file:
    json.dump(data,json_file,indent=2)   
