# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 15:37:07 2020

@author: Greg.Moschonas
"""

import numpy as np
from scipy.special import factorial
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter 
    
def binomial_distribution_general(n: int=2, 
                                  Pyes: float=0.5) -> pd.DataFrame:
    '''
    Returns a pandas dataframe of and plots the binomial distribution for a 
    given number of trials
    
    Parameters
    ----------
    n : int, optional
        The number of trials. The default is 2.
    Pyes: float, optional
        The probability (0-1) of the desired outcome in the trial. 
        (e.g. 0.5 for the probability of getting heads in a coin toss)
        The default is 0.5 

    Returns
    -------
    pd.DataFrame.
    
    Example
    # A pizza is cut into four slices of equal area. Ten identical pieces of 
    # chilli are randomly tossed onto the pizza. Each toss is completely random 
    # so that no single toss influences the result of any other. Therefore, 
    # single tosses are independent trials. In each trial, the probability that 
    # the centroid of a piece of chilli lands on a specific slice is 0.25 and 
    # the probability that it lands on the remaining three slices is 0.75. The 
    # probability distribution of the number of chilli pieces (their centroids) 
    # that land on the specific slice (hot!) after all 10 have been tossed 
    # onto the pizza can be calculated.
    
    >>> chilli_pizza = binomial_distribution_general(10, 1/4)
    >>> chilli_pizza
         probability      cum_prob
    X                             
    10  9.536743e-07  9.536743e-07
    9   2.861023e-05  2.956390e-05
    8   3.862381e-04  4.158020e-04
    7   3.089905e-03  3.505707e-03
    6   1.622200e-02  1.972771e-02
    0   5.631351e-02  7.604122e-02
    5   5.839920e-02  1.344404e-01
    4   1.459980e-01  2.804384e-01
    1   1.877117e-01  4.681501e-01
    3   2.502823e-01  7.184324e-01
    2   2.815676e-01  1.000000e+00
    
    >>> chilli_pizza[chilli_pizza['cum_prob'] <= 0.05]
         probability      cum_prob
    X                             
    10  9.536743e-07  9.536743e-07
    9   2.861023e-05  2.956390e-05
    8   3.862381e-04  4.158020e-04
    7   3.089905e-03  3.505707e-03
    6   1.622200e-02  1.972771e-02
    '''
    # experiment: repeat a trial that has only two possible outcomes n times
    # outcomes of single trial {Y, N}
    # probability of outcomes of single trial P(Y), P(N) = P(not Y) =  1 - P(Y)
    # each trial is indepedent and P(Y) and P(N) remain constant between trials 
    
    # If one repeats the trial n times:
    # 1. The probability of those outcomes that have r number of Y is 
    # P(Y)**r * P(N)**(n-r) = P(Y)**r * (1-P(Y))**(n-r)
    # 2. the number of outcomes with r number of Y is
    # nCr. nCr = n!/(n-r)!r!
    # Therefore, the probability of getting r number of
    # heads (or tails) is P(Y)**r * (1-P(Y))**(n-r) * nCr
    
    # Calculate the array of probabilities
    n_yes = np.arange(n+1)
    n_yes_probability = Pyes**n_yes * (1-Pyes)**(n-n_yes) * (factorial(n)/
                                                     (factorial(n - n_yes) * 
                                                      factorial(n_yes)))
    # Tidy up in a pandas dataframe
    binomial = pd.DataFrame({'X': n_yes,
                             'probability' : n_yes_probability})
    binomial.set_index('X', inplace=True)
    binomial = binomial.sort_values(by='probability')
    binomial['cum_prob'] = binomial['probability'].cumsum()

    
    # Probability distribution plot
    fig, ax = plt.subplots(figsize=[10,10])
    rects = ax.bar(binomial.index, 
                   binomial['probability'])
    ax.set(xticks=binomial.index,
           title='Probability distribution',
           xlabel='X', 
           ylabel='probability') 
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    
    def autolabel(rects):
        """
        Attach a text label above each bar in *rects*, displaying its height.
        """
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{:.1f}%'.format(height*100),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    if len(n_yes_probability) < 16:
        autolabel(rects)
    
    return binomial    
    
    