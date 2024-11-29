import numpy as np
import tomlkit
from copy import copy
import matplotlib.pyplot as plt
from importlib_resources import files
from pathlib import Path
from glob import glob
from itertools import cycle

data = files('data')
metadata_file = str(data.joinpath("result_metadata.toml"))

#default_values = dict(
#    independent_variable="wimp_mass",
#    units_independent_variable="GeV/c^2",
#    units_dependent_variable="cm^2",
#    header=["wimp_mass", "upper_limit"],  # use this to choose columns
#    delimiter=","  # change this if some .csv uses other format
#)
with open(metadata_file, "r") as f:
    metadata = tomlkit.load(f)
default_values = metadata["default_values"]


def find_dd_results(result_key="*.csv", require_metadata = False):
    possible_results  = glob(str(data.joinpath(result_key)))
    possible_results += glob("./"+result_key)
    print(possible_results)
    if len(possible_results) == 0:
            raise FileNotFoundError("No data .csv matching {:s}".format(str(data.joinpath(result_key))))
    print("{:d} files match your query:".format(len(possible_results)))
    
    ret = dict()
    for fn in possible_results:
        key = Path(fn).stem
        try:
            ret[key] = DD_result(fn)
        except Exception as e:
            print("Unable to load {:s}; {:s}".format(fn, str(e)))
            #ret[key] = {'description':'unable to load {:s}, error: {:s}'.format(fn, str(e))}

    print("Loaded {:d} files:".format(len(ret)))
    for k in sorted(ret.keys()):
        description = ret[k].get("description",k + " no metadata")
        if description == "":
            description = k + "no metadata"
        print(description)
    return ret



class DD_result:
    collected_lines = dict() # dict to store matplotlib line objects for legend-making
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
        possible_results+= glob("./"+result_key)
        if len(possible_results) == 1:
            self.load(possible_results[0])
        elif len(possible_results) == 0:
            raise FileNotFoundError("No data .csv matching {:s}".format(str(data.joinpath(result_key))))
        elif 1 < len(possible_results):
            raise ValueError("several files match pattern: "+str(possible_results))

    def load(self, filename):
        values = copy(default_values)
        key = Path(filename).stem
        self.key = key
        with open(metadata_file, "r") as f:
            metadata = tomlkit.load(f)
        values.update(metadata.get(key, dict()))
        for k, i in values.items():
            self[k] = i

        result_file = np.loadtxt(filename, delimiter=self.delimiter)
        for i, column_name in enumerate(self.header):
            mult = 1.
            if column_name != self.independent_variable:
                mult = self.scaling
                if mult != 1:
                    print("colname, idvname")
                    print(column_name, self.independent_variable)
            self[column_name] = mult*result_file[:, i]

    def plot(self, plot_variable="upper_limit", **plot_kwargs):
        args = dict(
            label=self.get("plot_label", ""),
            color=self.get("plot_color", "k")
        )
        args.update(**plot_kwargs)
        x = self[self.independent_variable]
        y = self[plot_variable]
        line, = plt.plot(x, y, **args)
        xd = self.get("label_range_down", x[0])
        xu = self.get("label_range_up", x[-1])
        self.collected_lines[self.key + plot_variable] = line, (xd,xu) , np.min(y), self.get("label","")

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

    @classmethod
    def add_line_legends(self, position_overrides=dict(),
                         xmin = -np.inf, xmax=np.inf,
                         outline_width=2, outline_color="auto",
                         **label_args):
        from labellines import labelLine
        ks = np.array(sorted(self.collected_lines.keys()))
        mins = [self.collected_lines[k][2] for k in ks]
        sis = np.argsort(mins)
        # Now the lines are sorted by their values:
        i_cycler = cycle([[0, 1.2], [1, 0.9]])
        ks = ks[sis]
        for k, (xi, xscale) in zip(ks, i_cycler):
            try:
                line, x, miny, label = self.collected_lines[k]
                x = [max(x[0], xmin), min(x[1], xmax)]
                xpos = position_overrides.get(k, x[xi]*xscale)
                labelLine(line, xpos, outline_width = outline_width, 
                          outline_color = outline_color, **label_args)
            except Exception as e:
                print(k, e)
