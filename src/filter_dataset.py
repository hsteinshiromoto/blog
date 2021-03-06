import dask.dataframe
import dask.dataframe as dd
import pandas as pd
import numpy as np
from math import log, e
import pretty_errors
from typing import Union
pd.util.testing.N = 100
pd.util.testing.K = 50


def entropy(data, base: int=None) -> float:
    """
    Computes entropy of label distribution. 

    Args:
        data ([array-like]): Iterable containing data
        base ([int], optional): Base of logarithm to calculate entropy. Defaults to None.

    Returns:
        [float]: Information entropy of data

    Example:
        >>> entropy(np.ones(5))
        0

    References:
        [1] https://stackoverflow.com/questions/15450192/fastest-way-to-compute-entropy-in-python
    """    

    n_labels = len(data)

    if n_labels <= 1:
        return 0

    value, counts = np.unique(data, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.

    # Compute entropy
    base = e if base is None else base
    for i in probs:
        ent -= i * log(i, base)

    return ent


def filter_nulls(data: dask.dataframe, nulls_threshold: float=0.75):
    """
    Filter data set based on proportion of missing values

    Args:
        data (dask.dataframe): Data set to be filtered
        nulls_threshold (float, optional): Proportion of maximum number of missing values. Defaults to 0.75.

    Example:
        >>> data = dd.from_pandas(pd.DataFrame(np.random.rand(100, 20)), npartitions=1)
        >>> filtered_data, summary = filter_nulls(data)
        >>> isinstance(summary, pd.DataFrame)
        True
        >>> summary.shape[0] == 20
        True

    Returns:
        Union[dask.dataframe, pd.DataFrame]: Filtered data, summary of missing values
    """

    summary_df = data.isnull().sum().compute()
    summary_df = summary_df.to_frame(name="nulls_count")
    summary_df["nulls_proportions"] = summary_df["nulls_count"] / data.shape[0].compute()
    summary_df.sort_values(by="nulls_count", ascending=False, inplace=True)

    mask_nulls = summary_df["nulls_proportions"] > nulls_threshold
    summary_df.loc[mask_nulls, "filtered_nulls"]  = 1
    summary_df.loc[~mask_nulls, "filtered_nulls"]  = 0
    
    removed_cols = list(summary_df[mask_nulls].index.values)

    return data.drop(labels=removed_cols, axis=1), summary_df



def filter_numerical_variance(data: dask.dataframe, 
                                std_thresholds: list=[0, np.inf], 
                                inclusive: bool=False):
    """
    Filter data set based on standard deviation of numerical values

    Args:
        data (dask.dataframe): Data set to be filtered
        variance_thresholds (list, optional): Standard deviation thresholds used to filter the data. Defaults to [0, np.inf].
        inclusive (bool, optional): Includes end points of the standard deviation thresholds. Defaults to False.

    Example:
        >>> data = dd.from_pandas(pd.DataFrame(np.random.rand(100, 20)), npartitions=1)
        >>> filtered_data, summary = filter_numerical_variance(data)
        >>> isinstance(summary, pd.DataFrame)
        True


    Returns:
        Union[dask.dataframe, pd.DataFrame]: Filtered data, summary of numerical columns
    """
    summary_df = data.select_dtypes(include=[np.number]).describe().compute()
    summary_df = summary_df.T.reset_index()
    summary_df.rename(columns={"index": "column_name"}, inplace=True)
    summary_df.sort_values(by="column_name", inplace=True)

    thresholds = [float(value) for value in std_thresholds]
    mask_variance = summary_df["std"].between(min(thresholds), max(thresholds), inclusive=inclusive)

    removed_cols = list(summary_df.loc[~mask_variance, "column_name"].values)
    mask_removed = summary_df["column_name"].isin(removed_cols)
    
    summary_df.loc[mask_removed, "filtered_variance"]  = 1
    summary_df.loc[~mask_removed, "filtered_variance"]  = 0
    
    return data.drop(labels=removed_cols, axis=1), summary_df.set_index("column_name")


def filter_entropy(data: dask.dataframe, entropy_thresholds: list=[0, np.inf],
                    inclusive: bool=False):
    """
    Filter data set based on entropy

    Args:
        data (dask.dataframe): Data set to be filtered
        entropy_thresholds (list, optional): Entropy value thresholds used to filter the data. Defaults to [0, np.inf].
        inclusive (bool, optional): Includes end points of the standard deviation thresholds. Defaults to False.

    Returns:
        Union[dask.dataframe, pd.DataFrame]: Filtered data, summary of numerical columns
    """

    summary_df = data.select_dtypes(exclude=[np.number], include=["object"]).describe().compute()
    summary_df = summary_df.T

    entropies = data.select_dtypes(exclude=[np.number], include=["object"]).compute().apply(entropy, axis=0)
    entropies = entropies.to_frame(name="entropy")

    summary_df = summary_df.merge(entropies, left_index=True, right_index=True)

    summary_df.reset_index(inplace=True)
    summary_df.rename(columns={"index": "column_name"}, inplace=True)
    summary_df.sort_values(by="column_name", inplace=True)

    thresholds = [float(value) for value in entropy_thresholds]
    mask_entropy = summary_df["entropy"].between(min(thresholds), max(thresholds), inclusive=inclusive)
    removed_cols = list(summary_df.loc[~mask_entropy, "column_name"].values)
    mask_removed = summary_df["column_name"].isin(removed_cols)
    summary_df.loc[mask_removed, "filtered_entropy"]  = 1
    summary_df.loc[~mask_removed, "filtered_entropy"]  = 0
    
    return data.drop(labels=removed_cols, axis=1), summary_df.set_index("column_name")


def test_filter_dataset(data: dask.dataframe):

    df = pd.util.testing.makeMixedDataFrame()
    df = df.merge(df, left_index=True, right_index=True)
    df = dd.from_pandas(df, npartitions=1)

    df, summary = filter_nulls(df, 0.75)
    df, num_summary = filter_numerical_variance(df, [0, 100])
    summary = summary.merge(num_summary, left_index=True, right_index=True, how="left")
    df, summary_cat = filter_entropy(df)

    summary = summary.merge(summary_cat, left_index=True, right_index=True, how="left")


    summary["count"] = summary["count_x"].fillna(0) + summary["count_y"].fillna(0)


if __name__ == "__main__":
    print("OK")
