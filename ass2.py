''' Starting point for ANLP 2014 assignment 2: CKY parsing'''
import re
import cfg_fix
from cfg_fix import parse_grammar, Tree
from cky import CKY

def tokenise(tokenstring):
  '''Split a string into a list of tokens, treating punctuation as
  separate tokens, and splitting contractions into their parts.
  So for example "I'm leaving." --> ["I","'m","leaving","."]'''
  return re.findall(r"[a-zA-Z]+|'[a-z]+|[,.?;:()-]", tokenstring)


grammar=parse_grammar("""
S -> NP VP
NP -> Det Nom | Nom | NP PP
Det -> NP "'s"
Nom -> N SRel | N
VP -> Vi | Vt NP | VP PP
PP -> Prep NP
SRel -> Relpro VP
Det -> 'a' | 'the'
N -> 'fish' | 'frogs' | 'soup' | 'children' | 'books'
Prep -> 'in' | 'for'
Vt -> 'saw' | 'ate' | 'read'
Vi -> 'fish' | 'swim'
Relpro -> 'that'
""")

# print grammar
# chart=CKY(grammar)
# chart.parse("the frogs swim".split()) # Should use
#                                       # tokenise(s) once that's fixed
# chart.pprint()
# Use this grammar for the rest of the assignment

grammar2=parse_grammar([
"S -> Sdecl '.' | Simp '.' | Sq '?' ",
"Sdecl -> NP VP",
"Simp -> VP",
"Sq -> Sqyn | Swhadv",
"Sqyn -> Mod Sdecl | Aux Sdecl",
"Swhadv -> WhAdv Sqyn",
"Sc -> Subconj Sdecl",
"NP -> PropN | Pro | NP0 ",
"NP0 -> NP1 | NP0 PP",
"NP1 -> Det N2sc | N2mp | Sc",
"N2sc -> Adj N2sc | Nsc | N3 Nsc",
"N2mp -> Adj N2mp | Nmp | N3 Nmp",
"N3 -> N | N3 N",
"N -> Nsc | Nmp",
"VP -> VPi | VPt | VPdt | Mod VP | VP Adv | VP PP",
"VPi -> Vi",
"VPt -> Vt NP",
"VPdt -> VPo PP",
"VPdt -> VPio NP",
"VPo -> Vdt NP",
"VPio -> Vdt NP",
"PP -> Prep NP",
"Det -> 'a' | 'the'",
"Nmp -> 'salad' | 'mushrooms'", 
"Nsc -> 'book' | 'fork' | 'flight' | 'salad' | 'drawing'",
"Prep -> 'to' | 'with'",
"Vi -> 'ate'",
"Vt -> 'ate' | 'book' | 'Book' | 'gave' | 'told'",
"Vdt -> 'gave' | 'told' ",
"Subconj -> 'that'",
"Mod -> 'Can' | 'will'",
"Aux -> 'did' ",
"WhAdv -> 'Why'",
"PropN -> 'John' | 'Mary' | 'NYC' | 'London'",
"Adj -> 'nice' | 'drawing'",
"Pro -> 'you' | 'he'",
"Adv -> 'today'"
])

chart2=CKY(grammar2)

# Note, please do _not_ use the Tree.draw() method uncommented
# _anywhere in this file_ (you are encouraged to use it in preparing
# your report).

# Q5: Uncomment this once you've completed Q5
# chart.parse(tokenise("the frogs swim"),True)
# Q6 Uncomment the next three once when you're working on Q6
#chart.parse(tokenise("fish fish"))
#chart.pprint()
#chart.parse(tokenise("fish fish"),True)
# Q7
# for s in ["John gave a book to Mary.",
#           "John gave Mary a book.",
#           "John gave Mary a nice drawing book.",
#           "John ate salad with mushrooms with a fork.",
#           "Book a flight to NYC.",
#           "Can you book a flight to London?",
#           "Why did John book the flight?",
#           "John told Mary that he will book a flight today."]:
#     print s, chart2.parse(tokenise(s))

# Q8
for s in ["John gave a book to Mary.",
          "John gave Mary a book.",
          "John gave Mary a nice drawing book.",
          "John ate salad with mushrooms with a fork.",
          "Book a flight to NYC.",
          "Can you book a flight to London?",
          "Why did John book the flight?",
          "John told Mary that he will book a flight today."]:
    print s, chart2.parse(tokenise(s))
    print chart2.first_tree().pprint()

# Q9
# for s in [...]:
#     print s, chart2.parse(tokenise(s))
#     for tree in chart2.all_trees():
#         print tree.pprint()




