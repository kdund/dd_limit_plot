import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import fnmatch

DATA_PATH = "../data"

# TODO: Arrange the limit by energy? like GeV, MeV, etc.
# TODO: Arrange by more parameters? Like decades, type of experiments, etc.
# TODO: Convert json into CSV automatically. Probably use chatgpt?
# TODO: Is it possible to collect all of the limits automatially? How to link to data extraction tools (like WebPlotDigitizer?)

def get_file_path(experiment, data_path=DATA_PATH):
    """
    Retrieve the path of a given experiment name (input strings)
    """

    # Convert the experiment name to lower case for case-insensitive matching
    experiment = experiment.lower()  

    # Use a list comprehension to get all files in the data_path directory that contain the experiment name
    # fnmatch.fnmatch() is used to perform case-insensitive matching on the file names
    matches = [f for f in os.listdir(data_path) if fnmatch.fnmatch(f.lower(), f'*{experiment}*')]

    # If there are no matches or more than one match, print a message and raise a ValueError
    if len(matches) == 0 or len(matches) > 1:
        print("Multiple or no data found, please adjust your search.")
        # Print all matching file names
        for match in matches:
            print(match)
        # Raise a ValueError to indicate that the search was unsuccessful
        raise ValueError("Ambiguous/Null searching error")

    # If there is exactly one match, print the file name and return it
    print(f"Found file: {matches[0]}")
    return matches[0]

def get_limit_df(experiment):
    """
    Get the limit of a given experiment name as a DataFrame 
    """

    # Use the get_file_path function to get the file name that matches the experiment name
    file_name = get_file_path(experiment)

    # Combine the data path with the file name to get the full path to the file
    file_path = os.path.join(DATA_PATH, file_name)

    # Read the file as a DataFrame using pandas, specifying that we only want the first two columns and that the column names should be 'mass' and 'limit'
    df = pd.read_csv(file_path, usecols=[0, 1], names=['mass', 'limit'], header=None)

    # Check if the first row of the DataFrame is numeric
    # If it's not, it's probably a header and should be removed
    if not (pd.to_numeric(df.iloc[0], errors='coerce').notna().all()):
        df = df.iloc[1:]

    # Check again if the first row contains any string values
    if df.iloc[0].apply(type).eq(str).any():
        # If it does, drop the first row
        df = df.iloc[1:]

    # Convert all values in the DataFrame to floats
    df = df.applymap(float)

    # Return the DataFrame
    return df