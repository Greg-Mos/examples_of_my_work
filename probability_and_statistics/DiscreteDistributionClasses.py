# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 14:18:14 2020

@author: Greg.Moschonas
"""

import numpy as np
from scipy.special import comb, factorial
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter 
from scipy.stats import binom
from typing import List

class _DiscreteProbabilityDistribution():
    
    def __init__(self, parameters: dict):
        '''
        Let X be a random variable that represents a discrete quantity. 
        X is modelled with a dicrete probability distribution with parameters 
        'parameters'.
        
        Parameters
        ----------
        parameters : dict
            The parameters of the distribution

        Returns
        -------
        None.

        '''
        self.parameters = parameters
        self.pmf_formula = None
        self.cdf_formula = None
        self.mean_formula = None
        self.X_range = [-np.inf, np.inf]
        self.name = 'X~DPD(parameters)'
    
    def _check_value_is_in_range(self, x: int):
        if not ((self.X_range[0] <= x) and (x <=  self.X_range[1])):
            raise TypeError("{} is out of range {}".format(x, self.X_range))
        
        
    def pmf(self, x: List[int]) -> pd.core.frame.DataFrame:
        '''
        The probability mass function (p.m.f.) of the disrete probability
        distribution

        Parameters
        ----------
        x : List[int]
            Each x in the list will be treated as X=x in the p.m.f.
                                                         
        Returns
        -------
        A pandas Dataframe with columns 'x' and 'p(x)', where x is (X=x); 
        and p(x) is  P(X=x).
        
        '''
        if type(x) == int:
            y = [x]
        else:
            y = list(x)
        results = {'x' : [], 'p(x)' : []}
        for x in y:
            self._check_value_is_in_range(x)
            px = eval(self.pmf_formula)
            # px = round(px, 4)
            results['x'].append(x)
            results['p(x)'].append(px)
        return pd.DataFrame(results)
    
    def cdf(self, x: List[int]) -> pd.core.frame.DataFrame:
        '''
        The cumulative distribution function (c.d.f.) of the disrete 
        probability distribution

        Parameters
        ----------
        x : List[int]
            Each x in the list will be treated as X<=x in the c.d.f.
                                                         
        Returns
        -------
        A pandas Dataframe with columns 'x' , 'p(x)' and 'F(x)', where x is 
        (X=x); and F(x) is P(X<=x).

        '''
        if type(x) == int:
            y = [x]
        else:
            y = list(x)
        if self.cdf_formula == None:
            if self.X_range[0] != -np.inf:
                start = self.X_range[0]
            end = max(y) + 1
            cdf = self.pmf(list(range(start, end)))
            cdf['F(x)'] = cdf['p(x)'].cumsum()
            result = cdf[cdf['x'].isin(y)][['x','F(x)']]
        else:
            results = {'x' : [], 'F(x)' : []}
            for x in y:
                self._check_value_is_in_range(x)
                px = eval(self.cdf_formula)
                # px = round(px, 4)
                results['x'].append(x)
                results['F(x)'].append(px)
                result = pd.DataFrame(results)
        
        return result 
    
    def mean(self) -> float:
        '''
        The mean or expected value of the probability distribution

        Returns
        -------
        float.

        '''
        return eval(self.mean_formula)
    
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
        title = '{0} {1}'.format(function, self.name)
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
        
        if len(x) <= 21:
            autolabel(rects)
        return ax
    
    def pmf_of_range_with_plot(self, start: int, end: int):
        '''
        Parameters
        ----------
        start : int
            The start of the range (inclusive).
        end : int
            The end of the range (inclusive).

        Returns
        -------
        pmf : pd.core.frame.DataFrame
            The p.m.f over the entire range of X
        ax : matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes object of the bar chart depicting the p.m.f.

        '''

        pmf = self.pmf(list(range(start, end + 1)))
        ax = self._plot_discrete_distribution(pmf['x'], pmf['p(x)'])
        return pmf, ax
    
    def cdf_of_range_with_plot(self, start, end):
        '''
        Parameters
        ----------
        start : int
            The start of the range (inclusive).
        end : int
            The end of the range (inclusive).

        Returns
        -------
        cmf : pd.core.frame.DataFrame
            The c.d.f over the entire range of X
        ax : matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes object of the bar chart depicting the c.d.f.

        '''
        
        cdf = self.cdf(list(range(start, end + 1)))
        ax = self._plot_discrete_distribution(cdf['x'], cdf['F(x)'])
        return cdf, ax
    
class Bernoulli(_DiscreteProbabilityDistribution):
    
    def __init__(self, p: float):
        '''
        A Bernoulli trial is a single statisitcal experiment for which there
        are two possible outcomes. A Bernoulli random variable X with range 
        {0,1} has Bernoulli probability distribution with parameter p, 
        0 < p < 1, where p is the probability that X is a success. 
        X ~ Bernoulli(p).
        
        Parameters
        ----------
        p : float
            The probability of success in the Bernoulli trial.

        Returns
        -------
        None.

        '''
        super().__init__(parameters={'p': p})
        self.pmf_formula = ("self.parameters['p']**x *"
                            "(1-self.parameters['p'])**(1-x)")
        self.mean_formula = "1 * parameters['p']"
        self.X_range = [0, 1]
        self.name = 'X~Bernoulli({0})'.format(self.parameters['p'])
    
class Binomial(_DiscreteProbabilityDistribution):
    
    def __init__(self, n: int, p: float):
        '''
        Let X be a random variable that represents the total number of 
        successes in a sequence of n independent Bernoulli trials in which the 
        probability of success of each trial is equal to p. Then X can be 
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
        super().__init__(parameters={'n': n, 'p': p})
        self.pmf_formula = ("comb(self.parameters['n'], x) * "
                            "self.parameters['p']**x * "
                            "(1-self.parameters['p'])**"
                            "(self.parameters['n']-x)")
        self.mean_formula = "self.parameters['n'] * self.parameters['p']"
        self.X_range = [0, n]
        self.name = 'X~B({0},{1})'.format(self.parameters['n'], 
                                          self.parameters['p'])

class Geometric(_DiscreteProbabilityDistribution):
    
    def __init__(self, p: float):
        '''
        Let X be a random variable that represents the total number of trials 
        up to and including the first success in a sequence of independent 
        Bernoulli trials, in which the probability of success of each trial is 
        equal to p. Then X can be modelled with a geometric distribution with 
        parameter p:
        X ~ G(p).
        
        Parameters
        ----------
        p : float
            The probability of success in each Bernoulli trial.
            
        Returns
        -------
        None.

        '''
        super().__init__(parameters={'p': p})
        self.pmf_formula = ("(1-self.parameters['p'])**(x-1) * "
                            "self.parameters['p']")
        self.cdf_formula ="1-(1-self.parameters['p'])**(x)"
        self.mean_formula = "1 / self.parameters['p']"
        self.X_range = [1, np.inf]
        self.name = 'X~G({0})'.format(self.parameters['p'])        

class Poisson(_DiscreteProbabilityDistribution):
    
    def __init__(self, l: float):
        '''
        X ~ Poisson(l).
        
        Parameters
        ----------
        l : float
            The lambda parameter of the Poisson distribution.
            
        Returns
        -------
        None.

        '''
        super().__init__(parameters={'l': l})
        self.pmf_formula = ("self.parameters['l']**(x) / "
                            "factorial(x) * np.exp(-self.parameters['l'])")
        self.mean_formula = "1 * self.parameters['l']"
        self.X_range = [0, np.inf]
        self.name = 'X~Poisson({0})'.format(self.parameters['l'])   
        
class Uniform(_DiscreteProbabilityDistribution):
    
    def __init__(self, m: int, n: int):
        '''
        Let X be a discrete random variable with range m, m+1,..., n.
        If no possible value within the range is more probable than any other
        possible value, then X can be modelled with a uniform distribution with 
        parameters m and n:
        X ~ Uniform(m, n).
        
        Parameters
        ----------
        m : int
            The lowest value of the range.
        n : int
            The highest value of the range.
            
        Returns
        -------
        None.

        '''
        super().__init__(parameters={'m': m, 'n': n})
        self.pmf_formula = "1 / (self.parameters['n'] - self.parameters['m'] + 1)"
        self.cdf_formula = ("(x - self.parameters['m'] + 1) / "
                            "(self.parameters['n'] - self.parameters['m'] + 1)")
        self.mean_formula = "(self.parameters['n'] + self.parameters['m']) / 2"
        self.X_range = [self.parameters['m'], self.parameters['n']]
        self.name = 'X~Uniform({0}, {1})'.format(self.parameters['m'],
                                                 self.parameters['n']) 