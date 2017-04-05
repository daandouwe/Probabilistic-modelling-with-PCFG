from cfg import read_grammar_rules, WCFG
from rule import Rule
from symbol import is_terminal, is_nonterminal, make_symbol
from collections import defaultdict
from item import Item
from agenda import Agenda

def cky_axioms(cfg, sentence):
    """
    Axioms for CKY.
    
    Inference rule:
        -------------------- (X -> alpha) in cfg and 0 <= i < n
        [X -> * alpha, [i]]
    
    :param cfg: a context-free grammar (an instance of WCFG)
    :param sentence: the input sentence (as a list or tuple)
    :returns: a list of items
    """
    items = []
    for rule in cfg:
        for i in range(len(sentence)):  # from zero to n-1
            items.append(Item(rule, [i]))
    return items

def earley_axioms(cfg, sentence, start):
    """
    Axioms for Earley.

    Inference rule:
        -------------------- (S -> alpha) in cfgs
        [S -> * alpha, [0]] 

    :param cfg: a context-free grammar (an instance of WCFG)
    :param sentence: the input sentence (as a list or tuple)
    :returns: a list of items that are Earley axioms  
    """
    items = []
    for rule in cfg.get(start):
        items.append(Item(rule, [0]))
    return items

def predict(cfg, item):
    """
    Prediction for Earley.

    Inference rule:
        -------------------- (SS -> alpha) in cfgs
        [S -> * alpha, [0]] 

    :param cfg: a context-free grammar (an instance of WCFG)
    :param item: an active Item
    :returns: a list of predicted Items or None  
    """
    items = []
    rules = cfg.get(item.next)
    for rule in rules:
            items.append(Item(rule, [item.dot]))
    return items

def scan(item, sentence):
    """
    Scan a terminal (compatible with CKY and Earley).
    
    Inference rule:
    
        [X -> alpha * x beta, [i ... j]]
        ------------------------------------    sentence[j] == x
        [X -> alpha x * beta, [i ... j + 1]]
    
    :param item: an active Item
    :param sentence: a list/tuple of terminals
    :returns: an Item or None
    """
    assert is_terminal(item.next), 'Only terminal symbols can be scanned, got %s' % item.next
    if item.dot < len(sentence) and sentence[item.dot] == item.next:
        return item.advance(item.dot + 1)
    else:
        return None
    
def complete(item, agenda):
    """
    Move dot over nonterminals (compatible with CKY and Earley).
    
    Inference rule:
    
        [X -> alpha * Y beta, [i ... k]] [Y -> gamma *, [k ... j]]
        ----------------------------------------------------------
                 [X -> alpha Y * beta, [i ... j]]
                 
    :param item: an active Item.
        if `item` is complete, we advance the dot of incomplete passive items to `item.dot`
        otherwise, we check whether we know a set of positions J = {j1, j2, ..., jN} such that we can
        advance this item's dot to.
    :param agenda: an instance of Agenda
    :returns: a list of items
    """
    items = []
    if item.is_complete():
        # advance the dot for incomplete items waiting for item.lhs spanning from item.start
        for incomplete in agenda.waiting(item.lhs, item.start):
            items.append(incomplete.advance(item.dot))
    else:
        # look for completions of item.next spanning from item.dot
        ends = set()
        for complete in agenda.complete(item.next, item.dot):
            ends.add(complete.dot)
        # advance the dot of the input item for each position that complete a span
        for end in ends:
            items.append(item.advance(end))
    return items



def make_forest(complete_items):
    """
    Turn complete items into a WCFG.
    
    :param complete_items: complete items (iterable)
    :returns: a WCFG
    """
    forest = WCFG()
    for item in complete_items:
        lhs = make_symbol(item.lhs, item.start, item.dot)
        rhs = []
        for i, sym in enumerate(item.rule.rhs):
            rhs.append(make_symbol(sym, item.state(i), item.state(i + 1)))
        forest.add(Rule(lhs, rhs, item.rule.prob))
    return forest

def make_chart(complete_items, n):
    chart = [[defaultdict(list) for j in range(n)] for i in range(n)] # n by n matrix with edges
    for item in complete_items:
        chart[item.start][item.dot][item.lhs].append((item.rule, item.dots_))
    return chart
                
def cky(cfg, sentence):
    A = Agenda()
    for item in cky_axioms(cfg, sentence):
        A.push(item)
    while A:
        item = A.pop()
        if item.is_complete() or is_nonterminal(item.next):
            for new in complete(item, A):
                A.push(new)
        else:
            new = scan(item, sentence)
            if new is not None:
                A.push(new)
        A.make_passive(item)
    return make_forest(A.itercomplete())

def earley(cfg, sentence, start):
    A = Agenda()
    for item in earley_axioms(cfg, sentence, start):
        A.push(item)
    while len(A) > 0:
        item = A.pop()
        # print 'item is: {}'.format(item)
        # print 'next item is: {}'.format(item.next)
        if item.is_complete() or is_nonterminal(item.next):
            # print 'predict:'
            # print predict(cfg, item)
            # print '\n'
            for new in predict(cfg, item):
                # print new
                A.push(new)

            # print 'complete:'
            # print complete(item, A)
            # print '\n'
            for new in complete(item, A):
                # print 'complete {}'.format(new)
                A.push(new)
        else:
            # print 'scan:'
            new = scan(item, sentence)
            # print new
            # print '\n'
            if new is not None:
                A.push(new)
        A.make_passive(item)
    return make_forest(A.itercomplete())













    