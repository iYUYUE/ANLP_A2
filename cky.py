import sys,re
import nltk
from nltk.tree import *
from collections import defaultdict
import cfg_fix
from cfg_fix import parse_grammar, CFG
from pprint import pprint

class CKY:
    """A Cocke-Kasami-Younger (bottom-up) CFG parser.
    Goes beyond strict CKY's insistance on Chomsky Normal Form.
    In particular it allows arbitrary unary productions, not just NT->T
    ones: It also allows unary-to-binary, i.e. X -> Y where Y -> A B"""
    def __init__(self,grammar):
        '''Create a CKY parser for a particular grammar, an NLTK CFG
        consisting of unary and binary rules (no empty rules,
        no more than two symbols on the right-hand side'''
        self.verbose=False
        assert(isinstance(grammar,CFG))
        self.grammar=grammar
        # split and index the grammar
        self.buildIndices(grammar.productions())

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

    def parse(self,tokens,verbose=False):
        '''Initialise a matrix from the sentence,
        then parse it
        Optional verbose argument controls debugging output, defaults to False '''
        self.verbose=verbose
        self.words = tokens
        self.n = len(self.words)+1
        self.matrix = []
        # We index by row, then column
        #  So Y below is 1,2 and Z is 0,3
        #    1   2   3  ...
        # 0  X   X   Z
        # 1      Y   X
        # 2          X
        # ...
        for r in range(self.n-1):
             # rows
             row=[]
             for c in range(self.n):
                 # columns
                 if c>r:
                     # This is one we care about, add a cell
                     row.append(Cell())
                 else:
                     # just a filler
                     row.append(None)
             self.matrix.append(row)
        self.unary_fill()
        self.binary_scan()
        return self.grammar.start() in self.matrix[0][self.n-1].getLabelList('symbol')

    def unary_fill(self):
        '''Determine the possible non-terminals 
            that each terminal can result from. 
            Fill the results in the middle diagonal
            and print'''
        for r in range(self.n-1):
            # the middle diagonal
            cell=self.matrix[r][r+1]
            # initialize the cell
            word=self.words[r]
            cell.addLabel(Label(symbol=word))
            # recursively update the cell
            cell.unary_update(word,self.unary)
            # print out the possible non-terminals for each cell (terminal)
            if self.verbose:
                print "Unary branching rules at node (%s,%s):%s"%(r,r+1,cell.getLabelList('symbol'))

    def binary_scan(self):
        '''The heart of the parser:
            proceed across the upper-right diagonals
            in increasing order of constituent length'''
        for span in xrange(2, self.n):
            for start in xrange(self.n-span):
                end = start + span
                for mid in xrange(start+1, end):
                    self.maybe_build(start, mid, end)

    def maybe_build(self, start, mid, end):
        """
        Search for the possible combinitions of 
            the symbols in two given cells (one from each) to 
            match the rhs of binary branching rules
        """
        if self.verbose:
            print "Binary branching rules for %s--%s--%s:"%(start,mid,end),
        cell=self.matrix[start][end]
        # search from the given cells
        for s1 in self.matrix[start][mid].getLabelList('symbol'):
            for s2 in self.matrix[mid][end].getLabelList('symbol'):
                # for a binary branching rule match
                if (s1,s2) in self.binary:
                    # add all possible non-terminals from the lhs of the rule
                    for s in self.binary[(s1,s2)]:
                        if s not in cell.getLabelList('symbol'):
                            cell.addLabel(Label(symbol=s, start=start, end=end, rhs=[(mid,(s1,s2))]))
                            # add more possible non-terminals 
                            # because, in the grammar, there are unary rules 
                            # that can produce non-terminals
                            cell.unary_update(s,self.unary)
                        else:
                            cell.updateRHS('symbol',s,(mid,(s1,s2)))
                        if self.verbose:
                            print " %s -> %s %s"%(s, s1,s2),
        if self.verbose:
            print 

    def pprint(self,cell_width=8):
        '''Try to print matrix in a nicely lined-up way'''
        row_max_height=[0]*(self.n)
        col_max_width=[0]*(self.n)
        print_matrix=[]
        for r in range(self.n-1):
             # rows
             row=[]
             for c in range(r+1,self.n):
                 # columns
                 if c>r:
                     # This is one we care about, get a cell form
                     #  and tabulate width, height and update maxima
                     cf=self.matrix[r][c].str(cell_width)
                     nlines=len(cf)
                     if nlines>row_max_height[r]:
                         row_max_height[r]=nlines
                     if cf!=[]:
                         nchars=max(len(l) for l in cf)
                         if nchars>col_max_width[c]:
                             col_max_width[c]=nchars
                     row.append(cf)
             print_matrix.append(row)
        row_fmt='|'.join("%%%ss"%col_max_width[c] for c in range(1,self.n))
        row_index_len=len(str(self.n-2))
        row_index_fmt="%%%ss"%row_index_len
        row_div=(' '*(row_index_len+1))+(
            '+'.join(('-'*col_max_width[c]) for c in range(1,self.n)))
        print (' '*(row_index_len+1))+(' '.join(str(c).center(col_max_width[c])
                       for c in range(1,self.n)))
        for r in range(self.n-1):
            if r!=0:
                print row_div
            mrh=row_max_height[r]
            for l in range(mrh):
                print row_index_fmt%(str(r) if l==mrh/2 else ''),
                row_strs=['' for c in range(r)]
                row_strs+=[wtp(l,print_matrix[r][c],mrh) for c in range(self.n-(r+1))]
                print row_fmt%tuple(row_strs)


    def first_tree(self):
        """
        Construct an NLTK Tree for the 'first' complete parse
        as S out of all of the parses represented in the top-right-hand corner 
        of the chart's matrix after a successful run.
        """
        return self.update_trees(0,len(self.matrix[0])-1,'S')

    def update_trees(self,start,end,lhs):
        # print str(start) + '|' + str(end) + '|' + N2S(lhs)
        label = self.matrix[start][end].searchLabelList('symbol',lhs)
        if not hasattr(label,'rhs'):
            return self.update_children(start,end,lhs,'',True)
        else:
            for r in label.rhs:
                return self.update_children(start,end,lhs,r,False)


    def update_children(self,start,end,lhs,rhs,terminal):
        if(terminal):
                return lhs
        mid = rhs[0]
        if(mid<0):
            return Tree(lhs,[self.update_trees(start,end,rhs[1])])
        else:
            return Tree(lhs,[self.update_trees(start,mid,rhs[1][0]),self.update_trees(mid,end,rhs[1][1])])
                 
def wtp(l,subrows,maxrows):
    '''figure out what row or filler from within a cell
    to print so that the printed cell fills from
    the bottom.  l will be in range(mrh)'''
    offset=maxrows-len(subrows)
    if l>=offset:
        return subrows[l-offset]
    else:
        return ''

class Cell:
    '''A cell in a CKY matrix'''
    def __init__(self):
        self._labels=[]

    def __str__(self):
        return self.str()

    def str(self,width=8):
        '''Try to format labels in a rectangule,
        aiming for max-width as given, but only
        breaking between labels'''
        labs=self.getLabelList('symbol')
        n=len(labs)
        res=[]
        if n==0:
            return res
        i=0
        line=[]
        ll=-1
        while i<n:
            s=str(labs[i])
            m=len(s)
            if ll+m>width and ll!=-1:
                res.append(' '.join(line))
                line=[]
                ll=-1
            line.append(s)
            ll+=m+1
            i=i+1
        res.insert(0,' '.join(line))
        return res
    
    def addLabel(self,label):
        self._labels.append(label)

    def labels(self):
        return self._labels

    def unary_update(self,symbol,unaries):
        """
        Update the cell labels by adding non-terminals which expand as the given symbol
        """
        # if the symbol is a right hand-side of a unary production rule
        if symbol in unaries:
        	# add each of possible corresponding left hand-sides to the cell's labels
            for parent in unaries[symbol]:
                if parent not in self.getLabelList('symbol'):
                    self.addLabel(Label(symbol=parent, rhs=[(-1,symbol)]))
                    # a recursive call is needed because in the grammar not all
                    # unary productions are terminal productions
                    self.unary_update(parent,unaries)
                else:
                    self.updateRHS('symbol',parent,symbol)

    """
    Custom Utility Functions for Q7 & Q8
    """

    def getLabelList(self,att):
        """
        Get lable list from Label structure list with specified attribute
        """
        tmpList = []
        for item in self._labels:
            tmpList.append(getattr(item,att))
        return tmpList
    
    def searchLabelList(self,att,value):
        for item in self._labels:
            # print N2S(getattr(item,att)) + '|' + N2S(value)
            if(N2S(getattr(item,att))==N2S(value)):
                return item

    def updateRHS(self,att,value,newRHS):
        self.searchLabelList(att,value).rhs.append(newRHS)

def N2S(n):
    """
    Nonterminal to String
    """
    if type(n) is nltk.Nonterminal:
        return n.unicode_repr()
    else:
        return n

class Label:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)