import numpy as np
import matplotlib.pyplot as plt
from rule import Rule
from cfg import WCFG, read_grammar_rules
from parser import cky
from earley import earley
from symbol import make_symbol, is_nonterminal, is_terminal
from collections import defaultdict
from util import get_rules_by_rhs



def inside(forest, start):  # acyclic hypergraph
    """
    The inside recursion for acyclic hypergraphs.
    
    :param forest: an acyclic WCFG
    :param start: the start symbol (str)
    :returns: a dictionary mapping a symbol (terminal or noterminal) to its inside weight
    """
    I = dict()
    
    def get_inside(symbol):
        """computes inside recursively"""
        w = I.get(symbol, None)
        if w is not None:  # already computed
            return w
        incoming = forest.get(symbol, set())
        if len(incoming) == 0:  # terminals have already been handled, this must be a nonterminal dead end
            # store it to avoid repeating computation in the future
            I[symbol] = 0.0
            return 0.0
        # accumulate the inside contribution of each incoming edge
        w = 0.0
        for rule in incoming:
            k = rule.prob
            for child in rule.rhs:
                k *= get_inside(child)
            w += k
        # store it to avoid repeating computation in the future
        I[symbol] = w
        return w
    
    # handles terminals
    for sym in forest.terminals:
        I[sym] = 1.0
    # recursively solves the inside formula from the start symbol
    get_inside(start)
        
    return I

 def outside(forest, start, inside_dict):
    
    I = dict()
    
    def get_outside(symbol):
        w = I.get(symbol, None)
        if w is not None:  # already computed
            return w
        outgoing = get_rules_by_rhs(forest, symbol)
        beta = 0.0
        for rule in outgoing:
            k = rule.prob
            for child in rule.rhs:
                if child != symbol:
                    try:
                        alpha = inside_dict[child]
                    except KeyError:
                        # Not sure about this solution...
                        # If child is not in inside_dict then child was not seen in the top-down process
                        # of the inside algorithm, and hence there is no way to complete child into a 
                        # parse for the whole sentence. So beta should be 0.0
#                         print "key-error with {}".format(child)
                        alpha = 0.0
                    k *= alpha
            k *= get_outside(rule.lhs)
            beta += k
        I[symbol] = beta
        return beta
    
    I[start] = 1.0
    
    for sym in forest.terminals:
#         print "terminal: {}".format(sym)
        I[sym] = get_outside(sym)
    
    return I


def inside_outside(training_sents, grammar, start_sym='[E]'):
    f = defaultdict(float)
    for sent in training_sents:
        forest = cky(grammar, sent)
        goal = make_symbol(start_sym, 0, len(sent))
        I = inside(forest, goal)
        O = outside(forest, goal, I)     
        for rule in grammar:
            w = 0.0
            for instance in get_instances(rule, forest):
                k = rule.prob
                k *= O[instance.lhs]
                for child in instance.rhs:
                    try:
                        alpha = I[child]
                    except KeyError:
                        # same solution as in outside
                        alpha = 0.0
                    k *= alpha
                w += k
            f[rule] += w/I[goal]
    return f

def EM(training_sents, grammar, n, start_sym='[E]', prin=False):
    if prin == True:
        print "Initalized grammar:\n{}\n".format(grammar)
    step = 0
    while step < n:
        
        # E-step
        f = inside_outside(training_sents, grammar, start_sym=start_sym)
                
        #M-step
        new_grammar = WCFG()
        for rule in grammar:
            new_prob = f[rule]/sum([f[r] for r in grammar.get(rule.lhs)])
            new_grammar.add(Rule(rule.lhs, rule.rhs, new_prob))
        
        grammar = new_grammar
        
        step +=1   
    return grammar


def plot_EM(corpus, grammar, n, start_sym='[E]'):
    d = defaultdict(list)
    for rule in grammar:
        # make sure the dict entries do not depend on the rule probs
        ruled = Rule(rule.lhs, rule.rhs, 1.0)
        d[ruled].append(rule.prob)
    i = 0
    while i < n:
        print "round {}".format(i)
        new_grammar = EM(corpus1, grammar, 1, start_sym=start_sym, prin=False)
        for rule in new_grammar:
            ruled = Rule(rule.lhs, rule.rhs, 1.0)
            d[ruled].append(rule.prob)
       
        grammar = new_grammar
        i += 1
        
    for rule, prob in d.iteritems():
        plt.plot(range(n+1), prob)
    plt.show()