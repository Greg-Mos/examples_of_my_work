# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 15:46:17 2020

@author: Greg.Moschonas
"""


from numpy.random import default_rng
import matplotlib.pyplot as plt

def sampling_distribution_of_mean(n: int=25):
    '''
    Generates a histogram for the sampling distribution of the mean

    Parameters
    ----------
    n : int, optional
        The sample size. The default is 25.

    Returns
    -------
    list.
        The means of all random samples.

    '''
    # generate a random population that is at least 100,000 in size
    rng = default_rng()
    population = rng.random(1000000) * 50
    pop_mean = population.mean()
    # draw 10000 random samples from the population and calulate the mean for 
    # each sample
    sample_means = []
    for i in range(10000):
        sample_means.append(rng.choice(population, n).mean())
    # draw a histogram of the sample means
    fig, ax = plt.subplots(figsize=[10,10])
    ax.hist(sample_means, range=(0,50), bins=100)
    ax.axvline(pop_mean, color='black')
    title = ('Sampling distribution of the mean for samples of size ' 
             '{}\n from a population with mean {:.2f} (vertical line)').format(n, pop_mean)
    ax.set(title=title,
           yticks=[],
           xlabel='sample mean') 
    
    return sample_means
        
    