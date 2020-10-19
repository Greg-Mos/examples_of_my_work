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
from scipy.stats import binom
from typing import List

class Binomial():
    pmf_formula = 'p(x) = c(n,x) * p**x * (1-p)**(n-x)'
    
    def __init__(self, n: int, p: float):
        '''
        Let X be a random variable that represents the total number of 
        successes in a sequence of n independent Bernoulli trials in which the 
        probability of success of each trial in equal to p. Then X can be 
        modelled with a bimomial distribution with parameters n and p: 
        X ~ B(n,p).
        
        Parameters
        ----------
        n : int
            The number of independent Bernoulli trials.
        p : float
            The probability of success in each Bernoulli trial.

        Returns
        -------
        None.

        '''
        self.p = p
        self.n = n
        self.pmf_formula = 'p(x) = c({0},x) * {1}**x * ({2})**({0}-x)'.format(
            n, p, round(1-p, 4))
        self.X_range = list(range(n+1))
        
    def pmf(self, x: List[int]) -> pd.core.frame.DataFrame:
        '''
        The probability mass function (p.m.f.) of the binomial distribution

        Parameters
        ----------
        x : List[int]
            X is the random variable that represents the number of total 
            successes in a sequence of n independent Bernoulli trials, 
            with range {0,...,n). 
            Each x in the list will be treated as X=x in the p.m.f.
                                                         
        Returns
        -------
        A pandas Dataframe with columns 'x' and 'p(x)', where x is the number 
        of total successes: (X=x); and p(x) is the probability that the 
        number of total successes is x: P(X=x).
        
        '''
        x = list(x)
        results = {'x' : [], 'p(x)' : []}
        for value in x:
            px = self.p**value * (1-self.p)**(self.n-value) * (factorial(self.n)/
                                                     (factorial(self.n - value) * 
                                                      factorial(value)))
            # px = round(px, 4)
            results['x'].append(value)
            results['p(x)'].append(px)
        return pd.DataFrame(results)
    
    def cdf(self, x: List[int]) -> pd.core.frame.DataFrame:
        '''
        The cumulative distribution function (c.d.f.) of the binomial 
        distribution

        Parameters
        ----------
        x : List[int]
            X is the random variable that represents the number of total 
            successes in a sequence of n independent Bernoulli trials, 
            with range {0,...,n). 
            Each x in the list will be treated as X<=x in the c.d.f.
                                                         
        Returns
        -------
        A pandas Dataframe with columns 'x' , 'p(x)' and 'F(x)', where x is the 
        number of total successes: (X=x); and F(x) is the probability that the 
        number of total successes is smaller or equal to x: P(X<=x).

        '''
        x = list(x)
        cdf = self.pmf(list(range(max(x) + 1)))
        cdf['F(x)'] = cdf['p(x)'].cumsum()
        # criterion = cdf['x'].map(lambda y: y in x)
        result = cdf[cdf['x'].isin(x)][['x','F(x)']]
        return result 
    
    def _plot_discrete_distribution(self, 
                                    x: pd.core.series.Series, 
                                    y: pd.core.series.Series):
        '''
        Creates a bar chart of probability distribution

        Parameters
        ----------
        x : pd.core.series.Series
            The values of X.
        y : pd.core.series.Series
            The values of p(x) or F(x).

        Returns
        -------
        matplotlib.axes._subplots.AxesSubplot

        '''
        if y.name == 'p(x)':
            ylabel = 'p(x)'
            function = 'pmf'
        elif y.name == 'F(x)':
            ylabel = 'F(x)'
            function = 'cdf'
        title = '{0} X~B({1},{2})'.format(function, self.n, self.p)
        fig, ax = plt.subplots(figsize=[10,10])
        rects = ax.bar(x, y)
        ax.set(xticks=x,
           title=title,
           xlabel='x', 
           ylabel=ylabel)
        
        def autolabel(rects):
            '''
            Attach a text label above each bar in *rects*, displaying its 
            height.
            '''
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{:.1f}%'.format(height*100),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        if len(x) <= 20:
            autolabel(rects)
        return ax
    
    def pmf_of_range_with_plot(self):
        '''
        Returns
        -------
        pmf : pd.core.frame.DataFrame
            The p.m.f over the entire range of X
        ax : matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes object of the bar chart depicting the p.m.f.

        '''
        pmf = self.pmf(self.X_range)
        ax = self._plot_discrete_distribution(pmf['x'], pmf['p(x)'])
        return pmf, ax
    
    def cdf_of_range_with_plot(self):
        '''
        Returns
        -------
        cmf : pd.core.frame.DataFrame
            The c.d.f over the entire range of X
        ax : matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes object of the bar chart depicting the c.d.f.

        '''
        cdf = self.cdf(self.X_range)
        ax = self._plot_discrete_distribution(cdf['x'], cdf['F(x)'])
        return cdf, ax
    
    
    
def binomial_distribution(n: int=2, 
                          p: float=0.5) -> pd.DataFrame:
    '''
    Returns a pandas dataframe of and plots the binomial distribution for a 
    given number of trials
    
    Parameters
    ----------
    n : int, optional
        The number of trials. The default is 2.
    p: float, optional
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
    
    >>> chilli_pizza = binomial_distribution(10, 1/4)
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
    n_yes_probability = p**n_yes * (1-p)**(n-n_yes) * (factorial(n)/
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

# same process using scipy.stats.binom
def binomial_distribution_with_scipy(n: int=2, 
                                     p: float=0.5):
    rv = binom(n, p)
    x = list(range(n+1))
    y = rv.pmf(x)
    fig, ax = plt.subplots(figsize=[10,10])
    ax.bar(x, y)
    return y

