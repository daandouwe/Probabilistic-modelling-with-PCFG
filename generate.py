"""
Functions to generate corpora from PCFGs (in WCFG form),
and to generate rule probabilites for a CFG using a Dirichlet 
distribution.
"""
from rule import Rule
import numpy as np
from symbol import is_nonterminal

def generate_sample(grammar, items=('[E]',)):
    """
    Given a grammar returns a sentence from it using
    the probabilities specfied in the grammar.
    :param items: call the function with (start,) where 
                  start is the start symbol of the grammar
    :returns: a sentence from the language as a list
    """
    frags = []
    for item in items:
        if is_nonterminal(item):
            productions = grammar.get(item)
            ps = [production.prob for production in productions]
            random_index = np.argmax(np.random.multinomial(1, ps, size=1))
            prod = productions[random_index]
            frags.extend(generate_sample(grammar, items=prod.rhs))
        else:
            frags.append(item)
    return frags

# print generate_sample(G)

def generate_corpus(grammar, n, start=('[E]',),):
    """
    Generates a corpus using the grammar
    :param n: size of the corpus
    :params: same a s generate corpus
    :returns: a corpus in the form of a list
    """
    return [generate_sample(grammar, items=start) for i in range(n)]

# corpus1 = generate_corpus(G, 100)
# corpus2 = generate_corpus(G, 1000)
# corpus3 = generate_corpus(G, 10000)

# print corpus1

def initialize(grammar, alpha=20.0):
    """
    Takes a grammar and returns that grammar with 
    the probabilities replaced by random probabilities
    generated from a Dirichlet distribution.
    :param: alpha is the Dirichlet concentration parameter
    """
    init_grammar = WCFG()
    for nonterminal in grammar.nonterminals:
        rules = grammar.get(nonterminal)
        init_prob = np.random.dirichlet(len(rules)*[alpha])
        for i, rule in enumerate(rules):
            init_grammar.add(Rule(rule.lhs, rule.rhs, init_prob[i]))
    return init_grammar

# init_grammar = initialize(G)
# print init_grammar
# print G