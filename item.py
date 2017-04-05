"""
An item in a CKY/Earley program.
"""

class Item(object):
    """A dotted rule used in CKY/Earley."""
    
    def __init__(self, rule, dots):
        assert len(dots) > 0, 'I do not accept an empty list of dots'
        self.rule_ = rule
        self.dots_ = tuple(dots)
        
    def __eq__(self, other):
        return self.rule_ == other.rule_ and self.dots_ == other.dots_
    
    def __ne__(self, other):
        return not(self == other)
    
    def __hash__(self):
        return hash((self.rule_, self.dots_))
    
    def __repr__(self):
        return '{0} ||| {1}'.format(self.rule_, self.dots_)
    
    def __str__(self):
        return '{0} ||| {1}'.format(self.rule_, self.dots_)
    
    @property
    def lhs(self):
        return self.rule_.lhs
    
    @property
    def rule(self):
        return self.rule_
    
    @property
    def dot(self):
        return self.dots_[-1]
    
    @property
    def start(self):
        return self.dots_[0]
    
    @property
    def next(self):
        """return the symbol to the right of the dot (or None, if the item is complete)"""
        if self.is_complete():
            return None
        return self.rule_.rhs[len(self.dots_) - 1]
    
    def state(self, i):
        return self.dots_[i]

    def advance(self, dot):
        """return a new item with an extended sequence of dots"""
        return Item(self.rule_, self.dots_ + (dot,))
    
    def is_complete(self):
        """complete items are those whose dot reached the end of the RHS sequence"""
        return len(self.rule_.rhs) + 1 == len(self.dots_)    
    