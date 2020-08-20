# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 10:01:01 2020

@author: Greg.Moschonas
"""

from itertools import product
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Experiment: roll two or more fair six-sided dice
# Sample space: all possible outcomes of the roll
# Event: roll a certain sum (e.g. 5)

# Find the probability of the event happening
# P(E) = number of ways E can happen / number of possible outcomes or
# P(E) = number of sample points that satisfy E / number of all possible sample points

def probability_of_sums_from_rolling_dice(n_sides:int=6, n_dice:int=2):
    '''
    Plots the probability of getting each unique sum from a random dice roll
    and returns a pandas dataframe with all possible rolls and their sums

    Parameters
    ----------
    n_sides : int, optional
        The number of sides of the dice. The default is 6.
    n_dice : int, optional
        The number of dice. The default is 2.

    Returns
    -------
    pandas DataFrame.

    '''
    # Sample space from rolling one die
    die_outcomes = list(range(1, n_sides + 1))
    
    # Sample space from rolling two dice
    twodice_outcomes = list(product(die_outcomes, repeat=n_dice))
    
    # Map of possible outcomes from rolling two dice to the sum of each outcome
    outcome_sum_map = {}
    for outcome in twodice_outcomes:
        outcome_sum_map[str(outcome)] = sum(outcome)
    outcomes_df = pd.DataFrame({'Roll': list(outcome_sum_map.keys()), 
                                'Sum': list(outcome_sum_map.values())})
    probabilities = outcomes_df.groupby('Sum').nunique()['Roll'] / len(twodice_outcomes)
    
    # Probability distribution plot
    fig, ax = plt.subplots(figsize=[10,10])
    rects = ax.bar(probabilities.index, probabilities)
    ax.set(xticks=probabilities.index,
            title='Probability distribution',
            xlabel='sum', 
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
    autolabel(rects)
    
    return outcomes_df
    

    




