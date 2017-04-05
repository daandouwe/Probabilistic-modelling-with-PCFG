from collections import deque
from symbol import is_nonterminal

def viterbi(forest, I, start):
    Q = deque([start])
    d = []
    while Q:
        parent = Q.popleft()
        incoming = forest.get(parent)
        # here we will find the distribution over edges
        weights = [0.0] * len(incoming)
        for i, rule in enumerate(incoming):
            weights[i] = rule.prob
            for child in rule.rhs:
                weights[i] *= I[child]
        # here we select the edge that is the maximum of this distribution
        weight, selected = max(zip(weights, incoming))
        # we also need to queue the nonterminals in the tail of the edge
        for sym in selected.rhs:
            if is_nonterminal(sym):
                Q.append(sym)
        # and finally, add the selected edge to the derivation
        d.append(selected)
    return d

def counting(forest, start):  # acyclic hypergraph
    N = dict()
    
    def get_count(symbol):
        w = N.get(symbol, None)
        if w is not None:
            return w
        incoming = forest.get(symbol, set())
        if len(incoming) == 0:  # terminals have already been handled, this must be a nonterminal dead end
            N[symbol] = w
            return 0
        w = 0
        for rule in incoming:
            k = 1
            for child in rule.rhs:
                k *= get_count(child)
            w += k
        N[symbol] = w
        return w
    
    # handles terminals
    for sym in forest.terminals:
        N[sym] = 1
    # handles nonterminals
    #for sym in forest.nonterminals:
    #    get_inside(sym)
    get_count(start)
        
    return N
