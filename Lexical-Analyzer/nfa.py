# Name: nfa.py
# Author: Kenny Collins and Rocky Hidalgo
# Date: October 14, 2023
# Last Modified: October 31,2023
# Description: Driver Code for pa2 comp 370

import dfa  # imports your DFA class from pa1
import queue
from collections import deque

class NFA:
    """ Simulates an NFA """
    
    def __init__(self, nfa_filename = None):
        """
        Initializes NFA from the file whose name is
        nfa_filename. (So you should create an internal representation
        of the nfa.)
        """
        self.alphabet = []
        self.num_states = 1
        self.start_state = 1
        self.transition_function = {}
        self.accept_states = []
        if nfa_filename:
            file = open(nfa_filename, 'r')
            self.num_states = int(file.readline())
            self.alphabet = [letters for letters in file.readline().strip("\n")]
            # key [state, alphabet] value = [nextState]
            self.transition_function = {}
            line = file.readline().strip("\n")
            # loop ends at empty line before start and accept state
            while line != "":
                parts = [part for part in line.replace('\'', "").split(" ")]  # splits into an array removing apostrophe and splitting by space
                q1, c, q2 = int(parts[0]), parts[1], int(parts[2])
                if q1 in self.transition_function.keys():
                    self.transition_function[q1].append([q1, c, q2])
                else:
                    self.transition_function[q1] = [[q1, c, q2]]
                line = file.readline().strip("\n")

            self.start_state = int(file.readline().strip('\n'))
            self.accept_states = [int(num) for num in file.readline().split(" ")]
            file.close()

    def to_DFA(self):
        """
        Converts the "self" NFA into an equivalent DFA object
        and returns that DFA. The DFA object should be an
        instance of the DFA class that you defined in pa1. 
        The attributes (instance variables) of the DFA must conform to 
        the requirements laid out in the pa2 problem statement (and that are the same
        as the DFA file requirements specified in the pa1 problem statement).

        This function should not read in the NFA file again. It should
        create the DFA from the internal representation of the NFA that you 
        created in __init__.
        """

        # Convert NFA to an equivalent DFA
        equiv_dfa = dfa.DFA()

        reject = None
        current_state = 1
        
        equiv_dfa.start_state = current_state
        equiv_dfa.alphabet = self.alphabet
        start_states = [self.start_state]
       
        queue = deque([self.start_state])

        # Traces epsilon transitions from start state
        visited = set()
        while queue:
            current_nfa_state = queue.popleft()
            if current_nfa_state not in visited:
                visited.add(current_nfa_state)
                for t in self.transition_function.get(current_nfa_state, []):
                    if t[1] == 'e':
                        start_states.append(t[2])
                        queue.append(t[2])

        epsilon_closures = {}
        for state in range(1, self.num_states + 1):
            epsilon_closures[state] = self.compute_epsilon_closure(state)

        state_queue = deque([tuple(start_states)])
        new_states = [tuple(start_states)]
        equiv_dfa.accept_states = list(equiv_dfa.accept_states)

        # Set up reject variable "self.reject_id" and set to the first DFA state
        while state_queue:
            current_substate = state_queue.popleft()
            current_nfa_states = list(current_substate)
            equiv_dfa.transition_function[current_state] = []
            is_accept_state = False

            # Check to see if transition is not defined by NFA
            for letter in self.alphabet:
                next_states = []
                is_accept_state = any(substate in self.accept_states for substate in current_substate)
                for substrate in current_nfa_states:
                    for transit in self.transition_function.get(substrate, []):
                        if transit[1] == letter:
                            next_states.extend(epsilon_closures[transit[2]])
                next_states = list(set(next_states))

                if next_states:
                    if tuple(next_states) not in new_states:
                        new_states.append(tuple(next_states))
                        state_queue.append(tuple(next_states))

                    next_state_num = new_states.index(tuple(next_states)) + 1
                else:
                    if reject:
                        next_state_num = reject
                    else:
                        new_states.append(tuple(next_states))
                        state_queue.append(tuple(next_states))
                        next_state_num = len(new_states)
                        reject = next_state_num

                new_tran = [current_state, letter, next_state_num]
                equiv_dfa.transition_function[current_state].append(new_tran)

                if is_accept_state:
                    equiv_dfa.accept_states.append(current_state)

            current_state += 1

        equiv_dfa.num_states = len(new_states)
        
        return equiv_dfa

    def compute_epsilon_closure(self, state):
        """
        Computes the epsilon closure for the given NFA state.
        """
        epsilon_closure = set([state])
        queue = deque([state])
        while queue:
            current_state = queue.popleft()
            for t in self.transition_function.get(current_state, []):
                if t[1] == 'e' and t[2] not in epsilon_closure:
                    epsilon_closure.add(t[2])
                    queue.append(t[2])
        return tuple(sorted(epsilon_closure))
