import numpy as np
import tomlkit
from copy import copy
import matplotlib.pyplot as plt
from importlib_resources import files
from pathlib import Path
from glob import glob

data = files('data')
metadata_file = str(data.joinpath("result_metadata.toml"))

default_values = dict(
    independent_variable="wimp_mass",
    units_independent_variable="GeV/c^2",
    units_dependent_variable="cm^2",
    header=["wimp_mass", "upper_limit"],  # use this to choose columns
    delimiter=","  # change this if some .csv uses other format
)

def find_dd_results(result_key="*.csv"):
    possible_results = glob(str(data.joinpath(result_key)))
    if len(possible_results) == 0:
            raise FileNotFoundError("No data .csv matching {:s}".format(str(data.joinpath(result_key))))
    print("{:d} files match your query:".format(len(possible_results)))
    
    ret = dict()
    for fn in possible_results:
        key = Path(fn).stem
        try:
            ret[key] = DD_result(fn)
        except Exception as e:
            print("Unable to load {:s}".format(fn))
            #ret[key] = {'description':'unable to load {:s}, error: {:s}'.format(fn, str(e))}

    print("Loaded {:d} files:".format(len(ret)))
    for k in sorted(ret.keys()):
        description = ret[k].get("description",k + " no metadata")
        print(description)



class DD_result:
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        if hasattr(self, key):
            return self[key]
        else:
            return default

    def __init__(self, result_key=""):
        possible_results = glob(str(data.joinpath(result_key)))
        if len(possible_results) == 1:
            self.load(possible_results[0])
        elif len(possible_results) == 0:
            raise FileNotFoundError("No data .csv matching {:s}".format(str(data.joinpath(result_key))))
        elif 1 < len(possible_results):
            raise ValueError("several files match pattern: "+str(possible_results))

    def load(self, filename):
        values = copy(default_values)
        key = Path(filename).stem
        with open(metadata_file, "r") as f:
            metadata = tomlkit.load(f)
        values.update(metadata.get(key, dict()))
        for k, i in values.items():
            self[k] = i

        result_file = np.loadtxt(filename, delimiter=self.delimiter)
        for i, column_name in enumerate(self.header):
            self[column_name] = result_file[:, i]

    def plot(self, plot_variable="upper_limit", **plot_kwargs):
        args = dict(
            label=self.get("plot_label", "")
        )
        args.update(**plot_kwargs)
        plt.plot(self[self.independent_variable],
                 self[plot_variable], **args)

    def plot_upper_limit(self, **plot_kwargs):
        plot_kwargs["linestyle"] = plot_kwargs.get("linestyle", "-")
        self.plot("upper_limit", **plot_kwargs)

    def plot_sensitivity(self, **plot_kwargs):
        plot_kwargs["linestyle"] = plot_kwargs.get("linestyle", "--")
        self.plot("sensitivity_median", **plot_kwargs)

    def plot_band(self, lower_edge = "sensitivity_m1sigma", upper_edge = "sensitivity_p1sigma", **plot_kwargs):
        args = dict(
            edgecolor = "none"
        )
        args.update(plot_kwargs)
        x = self[self.independent_variable]
        if type(lower_edge) == str:
            y_dn = self[lower_edge]
        elif ~hasattr(lower_edge, '__len__'):
            y_dn = lower_edge * np.ones(len(x))
        else:
            y_dn = x
        if type(upper_edge) == str:
            y_up = self[upper_edge]
        elif ~hasattr(upper_edge, '__len__'):
            y_up = upper_edge * np.ones(len(x))
        else: 
            y_up = x
        
        plt.fill_between(x, y_dn, y_up, **args)
    def plot_brazil_band(self, color_1sigma = "yellow", color_2sigma = "darkgreen", **plot_kwargs):
        self.plot_band(lower_edge = "sensitivity_m2sigma",
                       upper_edge = "sensitivity_m1sigma",
                       color=color_2sigma, **plot_kwargs)
        self.plot_band(lower_edge = "sensitivity_p1sigma",
                       upper_edge = "sensitivity_p2sigma",
                       color=color_2sigma, **plot_kwargs)
        self.plot_band(lower_edge = "sensitivity_m1sigma",
                       upper_edge = "sensitivity_p1sigma",
                       color=color_1sigma, **plot_kwargs)
