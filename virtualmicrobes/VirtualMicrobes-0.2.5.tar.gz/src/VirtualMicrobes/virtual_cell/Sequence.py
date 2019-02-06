import math
import copy
from VirtualMicrobes.virtual_cell.PhyloUnit import AddInheritanceType
import VirtualMicrobes.simulation.class_settings as cs
import matplotlib as mpl
from collections import OrderedDict
from orderedset import OrderedSet
import warnings

def pretty_scoring_matrix(seq1, seq2, scoring_mat, width=4):
    print ''.rjust(2*width) + ''.join(map(lambda s: s.rjust(width), seq2))
    for i, r in enumerate(scoring_mat):
        scores = ''.join(map(lambda s: str(s).rjust(width),r))
        if i == 0:
            print ''.rjust(width) + scores
        else:
            print str(seq1[i-1]).rjust(width) + scores
    

class Sequence:

    """
     
    :version:
    :author:
    """
    __phylo_type = cs.phylo_types['Sequence']
    __metaclass__ = AddInheritanceType
    __slots__ = ['elements', 'flip_dict', 'sequence', 'check_binding']
    
    uid = 0

    def __init__(self, sequence, elements, length,
                 flip_dict, time_birth=0, **kwargs):

        if sequence is None:
            if length is not None:
                sequence = [ elements[0] for _ in range(length) ]
            else:
                warnings.warn('No sequence or sequence length given. Sequence set to None')

        super(Sequence, self).__init__(time_birth=time_birth, **kwargs)
        self.elements = elements
        self.flip_dict = flip_dict
        self.sequence = sequence
        self.check_binding = True
        
    def match(self,sequence, func):
        pass
    
    
    def best_match(self, s2, at_least=0, penalty=0.5, report=False):
        '''
        Finds the best match possible between self and s2 anywhere in both
        sequences, but only if the match score reaches at least a minimum
        threshold. If the returned score is below this threshold it is not
        guaranteed to be the best possible match. No gaps are allowed.
        
        :param s2: sequence to compare to
        :param at_least: the minimum score that should still be attainable by
        the scoring algorithm for it to proceed computing the scoring matrix
        :param penalty: mismatch penalty
        '''
        if at_least is None:
            at_least = len(s2)
        s1 = self.sequence
        m,(max_score, x_y_coords) = self.substring_scoring_matrix(s1, s2, at_least, penalty)
        if x_y_coords is not None:
            top_x, top_y = x_y_coords
            
            start_x = top_x
            # now find the start of the match, 
            for i in xrange(1, top_x):
                score = m[top_x - i][top_y - i]
                start_x -= 1 
                if score <= 0:
                    break
        
        if report:
            pretty_scoring_matrix(self.sequence, s2, m)
            print 'max score', max_score, 'at pos', x_y_coords
        
        return max_score
                
    @classmethod
    def substring_scoring_matrix(cls, s1, s2, at_least=0, penalty=0.5):
        '''
        Computes a scoring matrix for matching between 2 sequences. Starts with 
        a matrix filled in with all -1 . Comparisons between the strings continue
        as long as it is still possible to obtain the 'at_least' score when comparing the
        remainder of the strings. When the score is too low and the remaining substring length
        that can still be matched too short, the algorithm will stop, leaving the rest of the 
        scores uncomputed. In that case, the _max is not guaranteed to be the maximum attainable
        matching score.
        
        
        example matrix when matching sequences 0000000000 and 0000010100 with the default 
        mismatch penalty of 0.5 (penalty substracted from score attained up to that point).
        
                   0   0   0   0   0   0   0   0   0   0     <- sequence 1
               0   0   0   0   0   0   0   0   0   0   0
           0   0   1   1   1   1   1   1   1   1   1   1
           0   0   1   2   2   2   2   2   2   2   2   2
           0   0   1   2   3   3   3   3   3   3   3   3
           0   0   1   2   3   4   4   4   4   4   4   4
           0   0   1   2   3   4   5   5   5   5   5   5
           1   0   0 0.5 1.5 2.5 3.5 4.5 4.5 4.5 4.5 4.5
           0   0   1   1 1.5 2.5 3.5 4.5 5.5 5.5 5.5 5.5
           1   0   0 0.5 0.5 1.0 2.0 3.0 4.0 5.0 5.0 5.0
           0   0   1   1 1.5 1.5 2.0 3.0 4.0 5.0 6.0 6.0
           0   0   1   2   2 2.5 2.5 3.0 4.0 5.0 6.0 7.0
           
           ^
           |
        sequence 2
           
        sequence 1: 0000000000 sequence 2: 0000010100 match: 0.7
        '''
        
        m = [ [0]+ [-1] * (len(s2)) if i>0 else [0] * (1+ len(s2)) for i in xrange(1 + len(s1))]
        end_s1 = len(s1) + 1
        end_s2 = len(s2) + 1
        _max = 0, None
        max_x = 0 # maximum score at the current x-pos
        max_x_prev = 0
        for x in xrange(1, end_s1): #start at (x,y) = 1,1 because scores at x=0 and y=0 are fixed.
            max_x_prev = max_x
            max_x = 0            
            if (end_s1 - x) + 1 + max_x_prev  <  at_least: #stop if at_least cannot be reached anymore
                break
            for y in xrange(1, end_s2):                
                if (end_s2 - y ) + 1 + max_x_prev < at_least: #break if at_least cannot be reached in the rest of the y-range
                    break
                prev_score = m[x - 1][y - 1]
                if min((end_s1 - x) , (end_s2 - y)) + prev_score < at_least:
                    continue          
                
                score = prev_score          
                if s1[x - 1] == s2[y - 1]:
                    score += 1
                else:
                    score -= penalty
                    if score < 0:
                        score = 0
                if score > max_x: 
                    max_x = score 
                if score > _max[0]:
                    _max = score, (x,y)
                m[x][y] = score

        return m, _max
    
    def randomize(self, rand_gen=None):
        self.sequence = self.random_sequence(len(self), rand_gen)
    
    def random_sequence(self, n, rand_gen):
        '''
        Create random sequence of length n from `elements`.
        
        Parameters
        ----------
        n : int
            length of sequence
        rand_gen : RNG
        
        Returns
        -------
        sequence string
        '''
        return ''.join(rand_gen.choice(self.elements) for _ in xrange(n))
    
    def bit_flip(self, bit, flip_dict=None):
        if flip_dict is None:
            flip_dict = self.flip_dict
        return flip_dict[bit]
        
    def mutate_bits(self, nr=1, rand_gen=None):
        '''
        Mutates a given number of random bits in the sequence to new values,
        chosen from the set of elements (possible values) that a bit can take,
        randomly.
        
        :param nr: number of bits to mutate
        :param rand_gen: random generator 
        '''
        indices = rand_gen.sample(range(len(self.sequence)), int(nr))
        mutated_sequence = list(self.sequence)
        for i in indices:
            mutated_sequence[i] = self.bit_flip(mutated_sequence[i])#rand_gen.choice(self.elements)
        self.sequence = "".join(mutated_sequence)
        return self.sequence
    
    def mutate(self, rand_gen=None, change_magnitude=None):
        '''
        Mutates the sequence. 
        
        Number of bits to mutate is either 1 or an amount of bits determined by
        the probability per bit to be changed or a given number of bits,
        depending on the value of "change_magnitude". Sets the check_binding
        flag to indicate that the sequence should be checked for changed binding
        status.
        
        Parameters
        ----------
        rand_gen : RNG
        change_magnitude : float or int
            when < 1, it is a probability, otherwise it is
            assumed to be the number of bits that should be changed (rounded up to
            nearest integer).
            
        Returns
        -------
        newly mutated sequences
        '''
        if change_magnitude is None:
            self.mutate_bits(rand_gen=rand_gen)
        elif change_magnitude < 1.:
            self.mutate_bits(math.ceil(change_magnitude * len(self.sequence)),
                             rand_gen=rand_gen)
        else:
            self.mutate_bits(math.ceil(change_magnitude), rand_gen=rand_gen)
        self.check_binding = True
        return self.sequence
    
    def insert_mutate(self, pos, sequence_stretch, constant_length=True):
        '''
        Insert a sequence stretch into the current sequence.
        
        Sets the check_binding flag to indicate that the sequence should be
        checked for changed binding status.
        
        
        Parameters
        ----------
        pos : int
            position in current sequence to insert
        sequence_stretch : str
            stretch to be inserted
        constant_length : bool
            whether to truncate after insertion to maintain the original sequence length
        
        Returns
        -------
        newly mutated sequences
        '''
        _seq_list = list(self.sequence)
        _seq_list[pos:pos] = sequence_stretch
        if constant_length: 
            _seq_list = _seq_list[:len(self.sequence)]
        self.sequence = ''.join(_seq_list)
        self.check_binding = True
        return self.sequence
    
    def __len__(self):
        return len(self.sequence)
    
    def __str__(self):
        return self.sequence
    
    def _reproduction_copy(self, time):
        copied = super(Sequence, self)._copy(time=time, new_id=False)
        copied.sequence = self.sequence 
        copied.elements = self.elements
        copied.flip_dict = self.flip_dict
        copied.check_binding = self.check_binding
        return copied
    
    def _mutation_copy(self):
        mutant = super(Sequence, self)._copy(new_id=False)
        mutant.sequence = copy.copy(self.sequence) 
        mutant.elements = self.elements
        mutant.flip_dict = self.flip_dict
        mutant.check_binding = self.check_binding
        return mutant
    
    def _hgt_copy(self):
        copied = super(Sequence, self)._copy(new_id=False)
        copied.sequence = copy.copy(self.sequence) 
        copied.elements = self.elements
        copied.flip_dict = self.flip_dict
        copied.check_binding = True
        return copied
        
class Operator(Sequence):

    """
     

    :version:
    :author:
    """
    
    __slots__ = ['binding_sequences']
    
    def __init__(self,  sequence=None, length=None, elements=["0","1"], 
                 flip_dict={'0':'1', '1':'0'}, **kwargs):
        self.init_binding_sequences()
        super(Operator,self).__init__(sequence=sequence, length=length,
                                      elements=elements, flip_dict=flip_dict, **kwargs)
    def init_binding_sequences(self):
        '''A dictionary from binding sequences that bind to this operator to binding scores
        
        '''
        self.binding_sequences = OrderedDict() 
    
    def calc_score_for_bs(self, binding_site, minimum_score=1., report=False):
        at_least = minimum_score * len(binding_site.sequence)
        raw_score = self.best_match(binding_site.sequence, at_least, report=report)
        score = float(raw_score) / len(binding_site.sequence)
        return score
                
    def update_binding_sequences(self, all_binding_sequences, minimum_score):
        '''
        Find the Binding Sequences that match this Operator and update
        dictionaries accordingly. Matching depends on a threshold
        "minimum_score".
        
        :param binding_sequences: set of BS 
        :param minimum_score: threshold for calling a match between this
        Operator and a BS
        '''
        self.init_binding_sequences()
        for bs in all_binding_sequences:
            self.bind_to_bs(bs, minimum_score)    
        self.check_binding = False
        
    def bind_to_bs(self, bs, minimum_score, report=False):
        score = self.calc_score_for_bs(bs, minimum_score, report=report)
        if score is not None and score >= minimum_score:
            if report:
                print 'bs:', bs.sequence, 'op:', self.sequence, 'match:', score 
            bs.bound_operators.add(self)
            self.binding_sequences[bs] = score
        elif report:
            print 'bs:', bs.sequence, 'op:', self.sequence, 'do not match:', score 
            
    def inform_bss(self):
        for bs in list(self.binding_sequences):
            bs.remove_bound_operator(self)
            del self.binding_sequences[bs]
                    
    def clear_binding_sequences(self):
        self.init_binding_sequences()
        self.check_binding = True
        
    def remove_binding_sequence(self, bs):
        del self.binding_sequences[bs]

    def calculate_regulation(self):
        pass
    
    
    
    def _update_binding_sequences(self, orig_copy_bs_dict):
        new_binding_sequences = OrderedDict()
        for bs, score in self.binding_sequences.items():
            new_binding_sequences[orig_copy_bs_dict[bs]] = score
        self.binding_sequences = new_binding_sequences
        
    def _reproduction_copy(self, time):
        copied = super(Operator, self)._reproduction_copy(time)
        copied.binding_sequences = copy.copy(self.binding_sequences)
        return copied
    
    def _mutation_copy(self):
        mutant = super(Operator, self)._mutation_copy()
        mutant.init_binding_sequences()
        #atr_cls = self.binding_sequences.__class__
        #mutant.binding_sequences = atr_cls.__new__(atr_cls)
        return mutant
    
    def _hgt_copy(self):
        copied = super(Operator, self)._hgt_copy()
        copied.init_binding_sequences()
        #atr_cls = self.binding_sequences.__class__
        #copied.binding_sequences = atr_cls.__new__(atr_cls)
        return copied
    
    def toJSON(self, *args, **kwargs):
            
        d = {'name': 'Operator',
             'description': ('Operator:' + self.sequence + 
                             '<br>BSs: ' + ' '.join(map(lambda bs: bs.sequence, self.binding_sequences) ) ),
             'size': len(self.binding_sequences) + 1,
             'colour': mpl.colors.rgb2hex(mpl.colors.colorConverter.to_rgba('blue'))
             }
        return d 
    
class BindingSequence(Sequence):
    '''
    Binding sequence of a Transcription Factor
    '''
    __slots__ = ['bound_operators']
    
    def __init__(self, sequence=None, length=None, elements=["0","1"], 
                 flip_dict={'0':'1', '1':'0'} ,**kwargs):
        self.init_bound_operators() 
        super(BindingSequence,self).__init__(sequence=sequence, elements=elements, 
                                             length=length,flip_dict=flip_dict, **kwargs)
        
    def init_bound_operators(self):
        self.bound_operators = OrderedSet()
        
    def remove_bound_operator(self,op):
        self.bound_operators.remove(op)
    
    def clear_bound_operators(self):
        self.bound_operators = OrderedSet()
        self.check_binding = True
        
    def match_operators(self, operators, minimum_score):
        for op in operators:
            op.bind_to_bs(self, minimum_score)
        self.check_binding = False
        
    def inform_operators(self):
        for op in list(self.bound_operators):
            op.remove_binding_sequence(self)
            self.bound_operators.remove(op)
            
    def _update_bound_operators(self, orig_copy_op_dict):
        new_bound_operators = OrderedSet()
        for op in self.bound_operators:
            new_bound_operators.add(orig_copy_op_dict[op])
        self.bound_operators = new_bound_operators
            
    def _reproduction_copy(self, time):
        copied =  super(BindingSequence, self)._reproduction_copy(time)
        copied.bound_operators = copy.copy(self.bound_operators)
        return copied
                
    def _mutation_copy(self):
        mutant = super(BindingSequence, self)._mutation_copy()
        mutant.init_bound_operators()
        #atr_cls = self.bound_operators.__class__
        #mutant.bound_operators = atr_cls.__new__(atr_cls)
        return mutant
    
    def _hgt_copy(self):
        copied = super(BindingSequence, self)._hgt_copy()
        copied.init_bound_operators()
        #atr_cls = self.bound_operators.__class__
        #copied.bound_operators = atr_cls.__new__(atr_cls)
        return copied
    
    def toJSON(self, *args, **kwargs):
        
        d = {'name': 'BS',
             'description': ('BS:' + self.sequence + 
                             '<br>OPs: ' + ' '.join(map(lambda op: op.sequence, self.bound_operators) ) ),
             'size': len(self.bound_operators) + 1,
             'colour': mpl.colors.rgb2hex(mpl.colors.colorConverter.to_rgba('green'))
             }
        return d
    
if __name__ == '__main__':
    new_seq = Sequence("0000000000",["0","1"], {'0':'1', '1':'0'})
    print new_seq.best_match("1100000000", 6.5)
    
    #new_seq = Sequence("bbb",["a","b"])
    #print new_seq.best_match("bbaabb",0)
    
