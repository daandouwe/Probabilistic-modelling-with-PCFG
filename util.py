import numpy as np
from nltk import Tree
from collections import defaultdict
from cfg import WCFG, read_grammar_rules


def make_nltk_tree(derivation):
	"""return a nlt Tree object based on the derivation (list or tuple of Rules)."""
	d = defaultdict(None, ((r.lhs, r.rhs) for r in derivation))
	
	def make_tree(lhs):
		return Tree(lhs[1:-1], (child if child not in d else make_tree(child) for child in d[lhs]))
	
	return make_tree(derivation[0].lhs)

def checking_number_parses(n=100):
	number = list()
	for sentence in toy_corpus[0:n]:
		toy_forest = cky(toy_grammar, sentence)
		toy_goal = make_symbol('[S]', 0, len(sentence))
		N_toy = counting(toy_forest, toy_goal)
		number.append(N_toy[toy_goal])
	return number

G = WCFG(read_grammar_rules(open('examples/ambiguous', 'r')))


def get_rules_by_rhs(grammar, symbol):
	"""
	Helper function for function outside in inside-outside.py
	:param grammar: a WCFG
	:param symbol: a symbol object
	:returns: list of all rules in grammar with symbol in rhs 
	"""
	rules = []
	for rule in grammar:
		if symbol in rule.rhs:
			rules.append(rule)
	return rules

# print get_rules_by_rhs(forest2, '[T:2-5]')

def get_instances(rule, forest):
	"""
	Given a rule
	
	A -> B C 
	
	get_instances collects all instances of rules of the form
	
	[A:i-j] -> [B:i-k] [C:k-j] 
	
	from the forest and returns them in a list.
	"""
	instances = []
	for r in forest:
		if r.lhs[1] == rule.lhs[1] and len(r.rhs)==len(rule.rhs):
			test = []
			for i in range(len(r.rhs)):
				try:
					# if for example r.rhs[i] = '[A]' 
					v = r.rhs[i][1] == rule.rhs[i][1]
					test.append(v)
				except IndexError:
					# if for example r.rhs[i] = '*' 
					v = r.rhs[i][0] == rule.rhs[i][0]
					test.append(v)
			if np.all(test):
				instances.append(r)
	return instances

def difference_grammar(one, another):
	"""
	Calculate the difference in probabilities of two grammars.

	:param one: one WCFG
	:param another: another WCFG (same rules as one!)
	:returns: a WCFG with the difference in rule prob between one and another
	"""
	diff_grammar = WCFG()
	for rule in one:
		for r in another:
			if r.rhs == rule.rhs and r.lhs == rule.lhs:
				approx_prob = r.prob
				break
		diff_grammar.add(Rule(rule.lhs, rule.rhs, abs(rule.prob-approx_prob)))
	return diff_grammar


