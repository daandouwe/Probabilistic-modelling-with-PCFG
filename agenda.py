"""
An agenda of active/passive items in CKY/Ealery program.
"""

from collections import defaultdict

class Agenda(object):
    
    def __init__(self):
        # we are organising active items in a stack (last in first out)
        self._active = []
        # an item should never queue twice, thus we will manage a set of items which we have already seen
        self._seen = set()
        # we organise incomplete items by the symbols they wait for at a certain position
        # that is, if the key is a pair (Y, i)
        # the value is a set of items of the form
        # [X -> alpha * Y beta, [...i]]
        self._incomplete = defaultdict(set)  
        # we organise complete items by their LHS symbol spanning from a certain position
        # if the key is a pair (X, i)
        # then the value is a set of items of the form
        # [X -> gamma *, [i ... j]]
        self._complete = defaultdict(set)
        
    def __len__(self):
        """return the number of active items"""
        return len(self._active)
        
    def push(self, item):
        """push an item into the queue of active items"""
        if item not in self._seen:  # if an item has been seen before, we simply ignore it
            self._active.append(item)
            self._seen.add(item)
            return True
        return False
    
    def pop(self):
        """pop an active item"""
        assert len(self._active) > 0, 'I have no items left.'
        return self._active.pop()
    
    def make_passive(self, item):
        if item.is_complete():  # complete items offer a way to rewrite a certain LHS from a certain position
            self._complete[(item.lhs, item.start)].add(item)
        else:  # incomplete items are waiting for the completion of the symbol to the right of the dot
            self._incomplete[(item.next, item.dot)].add(item)
            
    def waiting(self, symbol, dot):
        """return items waiting for `symbol` spanning from `dot`"""
        return self._incomplete.get((symbol, dot), set())
    
    def complete(self, lhs, start):
        """return complete items whose LHS symbol is `lhs` spanning from `start`"""
        return self._complete.get((lhs, start), set())  
    
    def itercomplete(self):
        """an iterator over complete items in arbitrary order"""
        for items in self._complete.itervalues():
            for item in items:
                yield item
                
