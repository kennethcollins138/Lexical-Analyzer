# Name: dfa.py
# Author: Kenny Collins and Rocky Hidalgo
# Date: September 15, 2023
# Last Modified: October 6,2023
# Description: Driver Code for  pa1 comp 370
import sys

class FileFormatError(Exception):
    """
    Exception that is raised if the 
    input file to the DFA constructor
    is incorrectly formatted.
    """
  
    pass

class DFA:
    def __init__(self, *, filename=None):
        """
        Initializes DFA object from the dfa specification
        in named parameter filename.
        """
        self.num_states = 0
        self.alphabet = None
        self.start_state = None 
        self.transition_function = {}
        self.accept_states = set()

        if filename:
            try:
                with open(filename, 'r') as file:
                    lines = file.readlines()
                    
                    if not lines:
                        raise FileFormatError("Empty DFA file")
            
                # check first line for number of states
                try:
                    self.num_states = int(lines[0].strip())
                except ValueError as e:
                    raise FileFormatError("Number of states is not an int")
                
                # second line contains the alphabet
                if lines[1].strip() == "":
                    print("empty alphabet")
                    raise FileFormatError("Empty alphabet")

                #set the alphabet
                self.alphabet = [*lines[1].strip()]

                # Loop through the transition function lines       
                for line in lines[2:-2]:  # Exclude the first two and last two lines
                    parts = line.strip().split("'")
                    if len(parts) != 3:
                        print("transition function error")
                        raise FileFormatError("Incorrect transition function format")
                    q1, c, q2 = int(parts[0].strip()), parts[1], int(parts[2].strip()) #accounts for apostrophe dictating transition function
                    self.transition_function[(q1, c)] = q2
                    
                    if c not in self.alphabet:
                        print("not in alphabet")
                        raise FileFormatError("Incorrect transition function")
                    if q1 < 1 or q1 > self.num_states or q2 < 1 or q2 > self.num_states:
                        print("Too many states")
                        raise FileFormatError("Too many states")
                
                # Second to last line contains start state
                line = lines[-2].strip().split()

                #check that there is only one start state
                if len(line) == 1:
                    self.start_state = int(lines[-2].strip())

                    line = lines[-1].strip().split()
                    for part in line:
                        try:
                            self.accept_states.add(int(part))
                        except ValueError:
                            raise FileFormatError("Lines beyond Accept States in file.")
                else:
                    self.start_state = int(lines[-1].strip())
                
                # Make sure start state is 1 length
                if self.start_state < 1 or self.start_state >= self.num_states:
                    print("Start state")
                    raise FileFormatError("Incorrect start state.")
                
                file.close()
                
            except FileNotFoundError:
                print("File not found")
                raise FileNotFoundError(f"File not found: {filename}")
            

    def transition(self, state, symbol):
        """
        Returns the state to transition to from "state" on input symbol "symbol".
        state must be in the range 1, ..., num_states
        symbol must be in the alphabet
        the returned state must be in the range 1, ..., num_states
        """
        if (state, symbol) not in self.transition_function:
            return 1

        for transition in self.transition_function[state]:
            if transition[1] == symbol:
                return transition[2]
            
    def simulate(self, str):
        """
        Returns True if str is in the language of the DFA,
        and False if not.

        Assumes that all characters in str are in the alphabet 
        of the DFA.
        """
        

        self.current_state = self.start_state

        for c in list(str):
            for i in self.transition_function[self.current_state]:
                if c == i[1]:
                    self.current_state = i[2]
                    break
        
        if self.current_state in self.accept_states:
            return True
        else:
            return False

        #for symbol in str:
        #    if (current_state, symbol) not in self.transition_function:
        #        return False  # Transition not defined, input is not accepted
        #    current_state = self.transition_function[(current_state, symbol)]

        #return current_state in self.accept_states

if __name__ == "__main__":
    # You can run your dfa.py code directly from a
    # terminal command line:

    # Check for correct number of command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 pa1.py dfa_filename str")
        sys.exit(0)

    dfa = DFA(filename = sys.argv[1])
    str = sys.argv[2]
    ans = dfa.simulate(str)
    if ans:
        print(f"The string {str} is in the language of the DFA")
    else:
        print(f"The string {str} is in the language of the DFA")

