import numpy as np
import copy
def ADJBP(ndata):
    """
    Parameters
    ----------
    y : array-like, 1-d

    Returns
    -------
    isOutlier

    """
    isOutlier = 0
    lower = 0
    upper = 0
    a = -4
    b = 3
    whis = 1.5
    mc = np.apply_along_axis(medcouple, 0, ndata)
    sortedData = copy.deepcopy(ndata)
    sortedData.sort()
    q1 = sortedData[int(0.25 * len(sortedData))]
    q3 = sortedData[int(0.75 * len(sortedData))]
    if mc >= 0:
        vloadj = q1 - whis * np.exp(a * mc) * (q3 - q1)
        vhiadj = q3 + whis * np.exp(b * mc) * (q3 - q1)
    else:
        vloadj = q1 - whis * np.exp(-b * mc) * (q3 - q1)
        vhiadj = q3 + whis * np.exp(-a * mc) * (q3 - q1)

    loadj = np.extract([ndata >= vloadj], ndata)
    upadj = np.extract([ndata <= vhiadj], ndata)

    if len(loadj):
        loadj = min(loadj)
    else:
        loadj = q1

    if len(upadj):
        upadj = max(upadj)
    else:
        upadj = q3

    isOutlier = (ndata < loadj) | (ndata > upadj)

    return isOutlier


def medcouple(y):
    """
    Calculates the medcouple robust measure of skew.

    Parameters
    ----------
    y : array-like, 1-d

    Returns
    -------
    mc : float
        The medcouple statistic

    Notes
    -----
    The current algorithm requires a O(N**2) memory allocations, and so may
    not work for very large arrays (N>10000).

    """

    y = np.squeeze(np.asarray(y))
    if y.ndim != 1:
        raise ValueError("y must be squeezable to a 1-d array")

    y = np.sort(y)

    n = y.shape[0]
    if n % 2 == 0:
        mf = (y[n // 2 - 1] + y[n // 2]) / 2
    else:
        mf = y[(n - 1) // 2]

    z = y - mf
    lower = z[z <= 0.0]
    upper = z[z >= 0.0]
    upper = upper[:, None]
    standardization = upper - lower
    is_zero = np.logical_and(lower == 0.0, upper == 0.0)
    standardization[is_zero] = np.inf
    spread = upper + lower
    return np.median(spread / standardization)