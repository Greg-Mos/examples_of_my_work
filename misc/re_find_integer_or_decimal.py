# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 12:06:03 2020

@author: mosgr
"""

import re

def find_integer_or_decimal_in_text(text: str) -> list:
    '''
    Returns all the strings that match integer or decimal format in text
    
    Examples
    
    >>> find_integer_or_decimal_in_text('ab123cd')
    ['123']
    
    >>> find_integer_or_decimal_in_text('ab-123cd')
    ['-123']
    
    >>> find_integer_or_decimal_in_text('ab1.23cd')
    ['1.23']
    
    >>> find_integer_or_decimal_in_text('ab-1.23cd')
    ['-1.23']
    
    >>> find_integer_or_decimal_in_text('ab12.3cd')
    ['12.3']
    
    >>> find_integer_or_decimal_in_text('ab.123cd')
    ['.123']
    
    >>> find_integer_or_decimal_in_text('ab-.123cd')
    ['-.123']
    
    >>> find_integer_or_decimal_in_text('ab123.cd')
    ['123.']
    
    >>> find_integer_or_decimal_in_text('ab-123.cd')
    ['-123.']
    
    >>> find_integer_or_decimal_in_text('ab..123cd')
    ['.123']
    
    >>> find_integer_or_decimal_in_text('ab123..cd')
    ['123.']
    
    >>> find_integer_or_decimal_in_text('ab123cd45ef')
    ['123', '45']
    
    >>> find_integer_or_decimal_in_text('ab123cd4.5ef')
    ['123', '4.5']
    
    >>> find_integer_or_decimal_in_text('ab123cd.45ef')
    ['123', '.45']
    
    >>> find_integer_or_decimal_in_text('ab123cd45.ef')
    ['123', '45.']
    
    >>> find_integer_or_decimal_in_text('ab-1.234.5cd')
    ['-1.234', '.5']
    
    >>> find_integer_or_decimal_in_text('ab-.1234.5cd')
    ['-.1234', '.5']
    '''
    # re explanation
    # two options: 
    # 1.minus symbol (zero or one times), followed by number (one or more times), 
    # followed by dot (zero or one times),followed by number (zero or more times)
    # 2.minus symbol (zero or one times), followed by dot, 
    # followed by number (one or more times).
    
    return re.findall('-?\d+\.?\d*|-?\.\d+', text)
