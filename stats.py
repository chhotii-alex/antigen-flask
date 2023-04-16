from scipy.stats import kstest

# Kolmogorov-Smirnov test comparing distributions
def compare(list_a, list_b):
    res = kstest(list_a, list_b)
    return res.pvalue
