from collections import defaultdict, deque
from symbol import is_terminal
from rule import Rule
import math


class WCFG(object):

    def __init__(self, rules=[]):
        self._rules = []
        self._rules_by_lhs = defaultdict(list)
        self._terminals = set()
        self._nonterminals = set()
        for rule in rules:
            self.add(rule)

    def add(self, rule):
        self._rules.append(rule)
        self._rules_by_lhs[rule.lhs].append(rule)
        self._nonterminals.add(rule.lhs)
        for s in rule.rhs:
            if is_terminal(s):
                self._terminals.add(s)
            else:
                self._nonterminals.add(s)

    def update(self, rules):
        for rule in rules:
            self.add(rule)

    @property
    def nonterminals(self):
        return self._nonterminals

    @property
    def terminals(self):
        return self._terminals

    def __len__(self):
        return len(self._rules)

    def __getitem__(self, lhs):
        return self._rules_by_lhs.get(lhs, frozenset())

    def get(self, lhs, default=frozenset()):
        """rules whose LHS is the given symbol"""
        return self._rules_by_lhs.get(lhs, frozenset())

    def can_rewrite(self, lhs):
        """Whether a given nonterminal can be rewritten.

        This may differ from ``self.is_nonterminal(symbol)`` which returns whether a symbol belongs
        to the set of nonterminals of the grammar.
        """
        return lhs in self._rules_by_lhs

    def __iter__(self):
        """iterator over rules (in arbitrary order)"""
        return iter(self._rules)
    
    def iteritems(self):
        """iterator over pairs of the kind (LHS, rules rewriting LHS)"""
        return self._rules_by_lhs.iteritems()
    
    def __str__(self):
        lines = []
        for lhs, rules in self.iteritems():
            for rule in rules:
                lines.append(str(rule))
        return '\n'.join(lines)


def read_grammar_rules(istream):
    """Reads grammar rules formatted as 'LHS ||| RHS ||| PROB'."""
    for line in istream:
        line = line.strip()
        if not line:
            continue
        fields = line.split('|||')
        if len(fields) != 3:
            raise ValueError('I expected 3 fields: %s', fields)
        lhs = fields[0].strip()
        rhs = fields[1].strip().split()
        prob = float(fields[2].strip())
        yield Rule(lhs, rhs, prob)

