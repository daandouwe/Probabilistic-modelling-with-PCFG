"""
Sampling from the inverted CDF associated with p(t|x).
The conditional independence assumption central to PCFGs make them convenient for sampling by ancestral sampling.

The code below is very similar to the Viterbi code above, however, instead of maximising at each step, 
we draw a random edge from the distribution defined by their inside weights. 
"""
from collections import deque
import random

def ancestral_sample(forest, I, start):
    """
    Sampling from the inverted CDF associated with p(t|x).
    The conditional independence assumption central to PCFGs 
    make them convenient for sampling by ancestral sampling.

    The code below is very similar to the Viterbi code above, 
    however, instead of maximising at each step, we draw a random 
    edge from the distribution defined by their inside weights. 

    :param forest: a derrivation forest in WCFG form
    :param I: an inside dictionary
    :param start: the starting symbol
    """
    Q = deque([start])
    d = []
    while Q:
        parent = Q.popleft()
        incoming = forest.get(parent)
        # here we compute the distribution over edges
        weights = [0.0] * len(incoming)
        for i, rule in enumerate(incoming):
            weights[i] = rule.prob
            for child in rule.rhs:
                weights[i] *= I[child]
        # here we draw a random threshold (think of it as sampling from the inverted CDF)
        th = random.uniform(0, I[parent])
        # here we compute the CDF step by step and check
        # for which edge e whether cdf(e) > th
        total = 0.0
        selected = None
        back = None
        for w, rule in zip(weights, incoming):
            total += w
            if total > th:
                selected = rule
                break
            else:
                back = rule
        if selected is None:  # this is to deal with corner cases due to rounding problems
            selected = back
        # every nonterminal child of the selected edge must be added to the queue
        for sym in selected.rhs:
            if is_nonterminal(sym):
                Q.append(sym)
        d.append(selected)
    return d

"""
Helper functions for gibs_sample.
"""

def sample_thetas(alphas):
    """
    :param alphas: a dictionary with dictionaries. Nonterminal A as key. As values 
    a dictionary with rules R that start with nonerminal A as keys and the alpha_R 
    Dirichlet pseudocounts as value:
    
    alphas = {A: {A -> B C: alpha_{A -> B C}, A -> a: alpha_{A -> a}}, 
              B: {B -> b: alpha_{A -> B C},...},
              ...}
    
    :returns: thetas drawn from a Dirichlet(alpha_A) for each nonerminal A in the same format as alphas.
    """
    thetas = {}
    # for each A we sample theta_A independently
    for A in G.nonterminals: 
        alpha_A = [alphas[A][R] for R in G.get(A)]
        theta_A = np.random.dirichlet(alpha_A)
        thetas[A] = {R: theta_A[i] for i, R in enumerate(G.get(A))}
    return thetas

def update_grammar(G, thetas):
    """
    :param G: a WCFG grammar
    :param thetas: thetas_A for all nonterminals A in G in the (peculiar) format 
    as returned by sample_thetas
    :returns: a WCFG new_G with the old thetas replaced by the new thetas
    """
    new_G = WCFG()
    for A in G.nonterminals:
        for rule, new_theta in thetas[A].iteritems():
            new_G.add(Rule(rule.lhs, rule.rhs, new_theta))
    return new_G

def update_alphas(alphas, grammar, tree):
    for A in grammar.nonterminals:
        for rule in alphas[A]:
            alphas[A][rule] += len(get_instances(rule, tree))
    return alphas

def make_samples(G):
    samples = []
    for sentence in small_corpus:
        goal = make_symbol('[E]', 0, len(sentence))
        forest = cky(G, sentence)
#         forest = earley(G, sentence, '[E]')
        I = inside(forest, goal)
        samples.append(sample(forest, I, goal))
    return samples

def gibs_sample(n, G, alphas):
    # for plotting
    d = defaultdict(list)
    # saving the correct probs of the grammar
    for rule in G:
            ruled = Rule(rule.lhs, rule.rhs, None) # prob=None so we can find the rules 
            d[ruled].append(rule.prob)            # in the dict even as probs change
    
    for i in range(n):
        # sample p(theta|t,w,alpha)
        thetas = sample_thetas(alphas)
        # update G with these thetas
        new_G = update_grammar(G, thetas) 

        # sample p(t|theta,w,alpha)
        samples = make_samples(new_G) # for each w_i in the corpus sample one t_i based on new_G
        
        # saving thetas per rule for plotting 
        for rule in new_G:
            ruled = Rule(rule.lhs, rule.rhs, None)
            d[ruled].append(rule.prob)
            
        # update alpha with rule counts
        for tree in samples:
            new_alphas = update_alphas(alphas, G, tree) # need not use new_G here: probs play no roles
                                                        # grammar only needed to get rules by nonerminals
        G = new_G
        alphas = new_alphas
    
    # for plotting 
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 
              'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    i = 0
    for rule, prob in d.iteritems():
        # plot correct values with ---
        plt.plot(range(n+1), [prob[0]]*(n+1), '--', color=colors[i], )
        # plot gibs sample-path with solid line
        plt.plot(range(n+1), prob, color=colors[i])
        i += 1
    
    plt.show()
    plt.clf()
    
    return new_G, alphas

