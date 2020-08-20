# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 13:16:07 2020

@author: Greg.Moschonas
"""
import math

def calculate_number_of_permutations_or_combinations(n: int,
                                                     r: int,
                                                     order_matters: bool=True,
                                                     with_repetition: bool=True):
    '''
    Displays the type of operation, the mathematical formula that calculates 
    the number of permutations or combinations, and its result.
    
    Based on https://www.mathsisfun.com/combinatorics/combinations-permutations-calculator.html

    Parameters
    ----------
    n : int
        Types to choose from.
    r : int
        Number chosen.
    order_matters : bool, optional
        The default is True.
    with_repetition : bool, optional
        The default is True.

    '''
    # order matters: permutation
    if order_matters:
        # with replacement
        if with_repetition:
            # permutation: the formula is n**r
            print('Permutation with repetition')
            print('formula: n**r')
            print('number of permutations: ', n**r)
        # without replacement
        else:
            # permutation: the formula is n!/(n-r)!
            print('Permutation without repetition')
            print('formula: n!/(n-r)!')
            print('number of permutations: ', 
                  math.factorial(n) / math.factorial(n - r))
    # order does not matter: combination
    else:
        # with replacement
        if with_repetition:
            # combination: the formula is (r+n-1)!/r!(n-1)!
            print('Combination with repetition')
            print('formula: (r+n-1)!/r!(n-1)!')
            print('number of permutations: ', 
                  math.factorial(r + n - 1) / (math.factorial(r) * math.factorial(n - 1)))
        # without replacement
        else:
            # combination: the formula is n!/r!(n-r)!
            print('Combination without repetition')
            print('formula: n!/r!(n-r)!')
            print('number of permutations: ', 
                  math.factorial(n) / (math.factorial(r) * math.factorial(n - r)))                