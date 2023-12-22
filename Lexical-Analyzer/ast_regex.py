# Name: ast_regex.py
# Author: Kenny Collins and Rocky Hidalgo
# Date: December 3,2023
# Last Modified: December 3,2023
# Description: Ast handling code for psa3 comp 370


from nfa import NFA

class Node:
    def __init__(self, char):
        self.char = char

#Handling 3 different leaf nodes
class SymbolLeaf(Node):
    def __init__(self, operand):
        super().__init__(operand)
    def to_nfa(self):
        new_nfa = NFA()
        new_nfa.start_state, new_nfa.num_states = 1,2
        new_nfa.alphabet = [self.char]
        
        new_nfa.accept_states = [2]
        new_nfa.transition_function = {1:[[1,self.char,2]]}
        
        return new_nfa
        

class EpsilonLeaf(Node):
    def __init__(self, epsilon):
        super().__init__(epsilon)
    def to_nfa(self):
        new_nfa = NFA()
        new_nfa.start_state, new_nfa.num_states = 1,2
        new_nfa.alphabet = ['e']
        
        new_nfa.accept_states = [2]
        new_nfa.transition_function = {1:[[1,'e',2]]}
        
        return new_nfa
    
class EmptyLeaf(Node):
    def __init__(self, empty):
        super().__init__(empty)
        
    def to_nfa(self):
        #im pretty sure it shouldnt have an alphabet or transition function. Empty set confusion
        new_nfa = NFA()
        new_nfa.start_state, new_nfa.num_states = 1,1
        new_nfa.accept_states = []
        new_nfa.transition_function = {}
        new_nfa.alphabet = []
        
        return new_nfa

#Handling 3 interior node types
class ConcatInt(Node):
    def __init__(self, concat_symb, left, right):
        super().__init__(concat_symb)
        self.right = right
        self.left = left
        
    def to_nfa(self):
        """
        should create connect left child nfa's accept states with an epsilon to the right's start
        need to offset start state by the num states of left state. Boom new nfa
        """
        
        #since we are traversing dfs, offset is used to ensure each state is unique, every little NFA is unique
        #offset applied ot right child since the left is our leaf node
        left_nfa = self.left.to_nfa()
        right_nfa = self.right.to_nfa()

        offset = left_nfa.num_states
        left_nfa.num_states += right_nfa.num_states

        for state, transitions in right_nfa.transition_function.items():
            new_transitions = [[start + offset, tran, end + offset] for start, tran, end in transitions]
            left_nfa.transition_function[state + offset] = new_transitions

        for state in left_nfa.accept_states:
            left_nfa.transition_function.setdefault(state, []).append([state, 'e', right_nfa.start_state + offset])

        left_nfa.accept_states = [state + offset for state in right_nfa.accept_states]

        return left_nfa

class UnionInt(Node):
    def __init__(self, union_symb, left, right):
        super().__init__('|')
        self.right = right
        self.left = left
        
    def to_nfa(self):
        """
        Should epsilon into two different options based off of union operator. Start state epsilons into left side of union,
        and start state epsilons into right side of union. Big chillin got this
        """
        left_nfa = self.left.to_nfa()
        right_nfa = self.right.to_nfa()

        offset = left_nfa.num_states
        left_nfa.num_states += right_nfa.num_states

        for state, transitions in right_nfa.transition_function.items():
            new_transitions = [
                [start + offset, tran, end + offset] for [start, tran, end] in transitions
            ]
            left_nfa.transition_function[offset + state] = new_transitions

        right_nfa.start_state += offset
        right_nfa.accept_states = [val + offset for val in right_nfa.accept_states]
        
        new_start = left_nfa.num_states + 1   
        left_nfa.num_states += 1
        left_nfa.transition_function[new_start] = [[new_start, 'e', left_nfa.start_state],[new_start, 'e', right_nfa.start_state]]
        left_nfa.start_state = new_start
        left_nfa.accept_states += right_nfa.accept_states
        
        return left_nfa

class StarInt(Node):
    def __init__(self, star_symb, operand):
        super().__init__('*')
        self.left = operand
        
    def to_nfa(self):
        """
        Create new start state that is accept state. that epsilons to initial state and have the star character go to another accept state. I think.
        """
        operand_nfa = self.left.to_nfa()

        new_start = operand_nfa.num_states + 1
        operand_nfa.num_states += 1

        for state in operand_nfa.accept_states:
            operand_nfa.transition_function.setdefault(state, []).append([state, 'e', operand_nfa.start_state])

        operand_nfa.transition_function[new_start] = [[new_start, 'e', operand_nfa.start_state], [new_start, 'e', new_start]]
        operand_nfa.start_state = new_start
        operand_nfa.accept_states.append(new_start)

        return operand_nfa