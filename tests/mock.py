import pandas as pd
import numpy as np
from pprint import pprint

def make_dataset(nrows: float=100, specs: dict=None, missing: bool=False):

    if nrows <= 4:
        nrows = 5

    if not specs:
        specs = {"float": [nrows, np.random.randint(1, 4), np.random.rand()]
                ,"integer": [nrows, np.random.randint(1, 4), np.random.rand()]
                ,"categorical": [nrows, np.random.randint(1, 4), 0.75]
                ,"boolean": [nrows, np.random.randint(1, 4), np.random.rand()]
                ,"string": [nrows, np.random.randint(1, 4), np.random.rand()]
                }

    values = {}
    for col_type, col_spec in specs.items():
        if col_type == "float":
            for count in range(col_spec[1]):
                values[f"{col_type}_{count}"] = np.random.rand(col_spec[0], 1).flatten()

        elif col_type == "integer":
            for count in range(col_spec[1]):
                values[f"{col_type}_{count}"] = np.random.randint(np.random.randint(1e6), size=col_spec[0]).flatten()

        elif col_type == "categorical":
            for count in range(col_spec[1]):
                values[f"{col_type}_{count}"] = ["".join(category.flatten()) for category in np.random.choice(["A", "B", "C", "D"], size=(col_spec[0], 3))]

        elif col_type == "boolean":
            for count in range(col_spec[1]):
                values[f"{col_type}_{count}"] = [bool(item) for item in np.random.randint(2, size=col_spec[0])]

        elif col_type == "string":
            for count in range(col_spec[1]):
                values[f"{col_type}_{count}"] = ["".join(category.flatten()) for category in np.random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "X", "Y", "W", "Z"], size=(col_spec[0], col_spec[0]))]

    df = pd.DataFrame.from_dict(values)

    if missing:
        for col_type, col_spec in specs.items():
            selected_cols = [col for col in df.columns.values if col_type in col]
            for col in set(selected_cols):
                mask = df[col].sample(frac=col_spec[2]).index
                df.loc[mask, col] = np.nan

    return df


if __name__ == "__main__":
    df = make_dataset(missing=True)
    pprint(df)
