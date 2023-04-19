from scipy.stats import kstest
#from scipy.stats import wasserstein_distance

# Kolmogorov-Smirnov test comparing distributions
def compare(list_a, list_b, label_a="", label_b=""):
    res = kstest(list_a, list_b)
    ks_pvalue =  res.pvalue
    #distance = wasserstein_distance(list_a, list_b)
    #n = len(list_a) + len(list_b)
    #print("%f\t%f\t%f\t%s\t%s" % (ks_pvalue, distance, n, label_a, label_b))
    return ks_pvalue
