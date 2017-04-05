from collections import defaultdict

class Rule(object):

    def __init__(self, lhs, rhs, prob):
        """
        Constructs a Rule.
        @param lhs: the LHS nonterminal
        @param rhs: a sequence of RHS symbols
        @param prob: probability of the rule 
        @param span: a tuple indicating the span of the rule
        """
        self.lhs_ = lhs
        self.rhs_ = tuple(rhs)
        self.prob_ = prob

    def __eq__(self, other):
        return self.lhs_ == other.lhs_ and self.rhs_ == other.rhs_ and self.prob_ == other.prob_

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.lhs_, self.rhs_, self.prob_))

    def __repr__(self):
        return '%s -> %s (%s)' % (self.lhs_,
                ' '.join(str(sym) for sym in self.rhs_),
                self.prob_)

    @property
    def lhs(self):
        return self.lhs_

    @property
    def rhs(self):
        return self.rhs_
    
    @property
    def prob(self):
        return self.prob_

        