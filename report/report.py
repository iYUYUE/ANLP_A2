def buildIndices(self,productions):
""" Creates dictionaries for storing the production rules.
In each dictionary, the rhs of a rule is the key and and a list of all lhs
which expand as the rhs is the value."""
# create dictionaries for unary and binary rules
self.unary=defaultdict(list)
self.binary=defaultdict(list)
for production in productions:
# separate its right hand-side from its left hand-side
rhs=production.rhs()
lhs=production.lhs()
# the assumption about the rules is that rhs is non-empty
# and rhs has no more than 2 non-terminals
assert(len(rhs)>0 and len(rhs)<=2)
# if the rule is unary, add it's lhs to the unary dictionary under rhs key
if len(rhs)==1:
self.unary[rhs[0]].append(lhs)
# if the rule is binary, add it's lhs to the binary dictionary under rhs key
# because of the assertion we know that len(rhs)==2
else:
self.binary[rhs].append(lhs)

