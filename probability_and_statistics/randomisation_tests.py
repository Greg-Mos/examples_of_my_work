import itertools
import numpy as np
import statistics
import scipy.stats

def permutation_test(batch1: list, batch2: list, 
                     n_permutations: int,
                     tstat='statistics.mean(batch1)-statistics.mean(batch2)', 
                     one_sided: str=None) -> float:
    '''
    A simple permutation test, based on this article
    https://www.r-bloggers.com/what-is-a-permutation-test/
    
    Parameters
    ----------
    batch1 : list
        A batch of data.
    batch2 : list
        A batch of data.
    n_permutations: int
        The number of permutations from which the distribution of the test
        statistic will be built. It should be a large number (e.g. 10000).
    tstat : str, optional
        The test statistic. This is provided a string that is then
        evaluated within the function.
        The default is 'statistics.mean(batch1)-statistics.mean(batch2)'
    one_sided : str, optional
        Whether to run a positive ('+') or negative ('-') one-sided test. 
        The default is two-sided (None).

    Returns
    -------
    float
        The probability, p, that the null hypothesis is true.
        
    Example
    >>> permutation_test([10,9,11], [12,11,13], 10000, one_sided='-')
    The result should be close to 0.1

    '''
    # calculate the test statitic
    t_obs = eval(tstat)
    # combine the two batches into one  batch
    batch_all = batch1 + batch2
    # get n_permutations permutations of the combined batch
    permutations = []
    for i in range(n_permutations):
        permutations.append(tuple(np.random.permutation(batch_all)))
    # initialise the list that will hold the distribution of the test statistic
    t_distribution = []
    # modify the test statistic string for the loop
    tstat_temp = tstat.replace('batch', 'batch_temp')
    # loop through the permutations
    for permutation in permutations:
        # split each the permutation into two batches
        batch_temp1 = permutation[0:len(batch1)]
        batch_temp2 = permutation[len(batch1):]
        # append each test statistic to the distribution    
        t_distribution.append(eval(tstat_temp))
    # initialise a counter
    counter = 0
    # loop through each test stat in the distribution.
    # The following block can probably be vectorised using numpy
    # but I like it as it is because it spells out the process. 
    for t in t_distribution:
        # if two-sided test is selected
        if one_sided == None:
            # increase the counter if the absolute value of the observed 
            # test statitic is equal or larger than the  absolute value of any
            # possible test statitics
            if abs(t) >= abs(t_obs):
                counter = counter + 1
        # if negative one-sided test is selected
        elif one_sided == '-':
            # increase the counter if the value of the observed 
            # test statitic is equal or smaller than the value of any
            # possible test statitics
            if t <= t_obs:
                counter = counter + 1
        # if positive one-sided test is selected
        elif one_sided == '+':
            # increase the counter if the value of the observed 
            # test statitic is equal or larger than the value of any
            # possible test statitics
            if t >= t_obs:
                counter = counter + 1
    # find the p value of the test statitic in the distribution
    p = counter / len(t_distribution)
    return p

def combination_test(batch1: list, batch2: list, 
                     tstat='statistics.mean(batch1)-statistics.mean(batch2)', 
                     one_sided: str=None) -> float:
    '''
    A simple combination test, based on this article
    https://www.thoughtco.com/example-of-a-permutation-test-3997741
    
    It is a permutation test that uses all the possible permutations where 
    order doesn't matter (combinations) to calculate the distribution
    of the test statitic. Therefore, it is recommended for only
    small sample sizes (<=5) on a typical PC. 
    
    Parameters
    ----------
    batch1 : list
        A batch of data.
    batch2 : list
        A batch of data.
    tstat : str, optional
        The test statistic. This is provided a string that is then
        evaluated within the function.
        The default is 'statistics.mean(batch1)-statistics.mean(batch2)'
    one_sided : str, optional
        Whether to run a positive ('+') or negative ('-') one-sided test. 
        The default is two-sided (None).

    Returns
    -------
    float
        The probability, p, that the null hypothesis is true.
        
    Example
    >>> combination_test([10,9,11], [12,11,13], one_sided='-')
    0.1

    '''
    # calculate the test statitic
    t_obs = eval(tstat)
    # combine the two batches into one  batch
    batch_all = batch1 + batch2
    # assign indeces to each value of the combined batch
    batch_all_inds = range(len(batch_all))
    # find all possible index combinations of batch1
    permut = itertools.combinations(batch_all_inds, len(batch1))
    # initialise the list that will hold the distribution of the test statistic
    t_distribution = []
    # modify the test statistic string for the loop
    tstat_temp = tstat.replace('batch', 'batch_temp')
    # loop through all possible combinations of batch1
    for batch1_inds in permut:
        # get the indeces of the control batch for the current combination
        # as the difference in sets of indeces 
        batch2_inds = list(set(batch_all_inds) - set(batch1_inds))
        # construct batch1 from the indeces
        batch_temp1 = []
        for index in batch1_inds:
            batch_temp1.append(batch_all[index])
        # construct batch2 from the indeces 
        batch_temp2 = []
        for index in batch2_inds:
            batch_temp2.append(batch_all[index])
        # append the test statitic to the distribution    
        t_distribution.append(eval(tstat_temp))
    # initialise a counter
    counter = 0
    # loop through each test stat in the distribution
    for t in t_distribution:
        # if two-sided test is selected
        if one_sided == None:
            # increase the counter if the absolute value of the observed 
            # test statitic is equal or larger than the  absolute value of any
            # possible test statitics
            if abs(t) >= abs(t_obs):
                counter = counter + 1
        # if negative one-sided test is selected
        elif one_sided == '-':
            # increase the counter if the value of the observed 
            # test statitic is equal or smaller than the value of any
            # possible test statitics
            if t <= t_obs:
                counter = counter + 1
        # if positive one-sided test is selected
        elif one_sided == '+':
            # increase the counter if the value of the observed 
            # test statitic is equal or larger than the value of any
            # possible test statitics
            if t >= t_obs:
                counter = counter + 1
    # find the p value of the test statitic in the distribution
    p = counter / len(t_distribution)
    return p
