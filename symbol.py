
def is_terminal(symbol):
    """nonterminals are formatted as this: [X]"""
    return not is_nonterminal(symbol)

def is_nonterminal(symbol):
    """nonterminals are formatted as this: [X]"""
    return symbol[0] == '[' and symbol[-1] == ']'

def make_symbol(base_symbol, sfrom, sto):
    if sfrom is None and sto is None:
        return base_symbol
    return base_symbol if is_terminal(base_symbol) else '[%s:%s-%s]' % (base_symbol[1:-1], sfrom, sto)