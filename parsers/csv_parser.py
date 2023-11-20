import os

import pandas as pd


def parse(filepath):
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise FileNotFoundError(f"File does not exists or is not a file: {filepath}")

    if os.path.getsize(filepath) == 0:
        return tuple()

    df = pd.read_csv(filepath, header=None)
    for ix, row in df.iterrows():
        yield row[0]
