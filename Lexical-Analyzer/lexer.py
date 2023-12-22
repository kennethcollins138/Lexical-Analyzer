from ast_regex import *
import regex
from nfa import NFA
from dfa import DFA
from collections import deque

class InvalidToken(Exception):
    """ 
    Raised if while scanning for a token,
    the lexical analyzer cannot identify 
    a valid token, but there are still
    characters remaining in the input file
    """
    pass

class Lex:
    def __init__(self, regex_file, source_file):
        """
        Initializes a lexical analyzer.  regex_file
        contains specifications of the types of tokens
        (see problem assignment for format), and source_file
        is the text file that tokens are returned from.
        """
        with open(regex_file, "r") as current_file:
            #get alphabet from first line of file
            line = current_file.readline()
            self.alphabet = list(line[line.find('"') + 1: line.rfind('"')])

            token_line = current_file.readline().strip()
            self.regex_tokens = {}

            while token_line: #need to handle following, token (regex file-> regex_tokens)
                split_token_line = token_line.split(maxsplit=1)
                self.regex_tokens[split_token_line[0]] = split_token_line[1]
                token_line = current_file.readline().strip()

            self.dfa_tokens = {}
            for name, regex_string in self.regex_tokens.items():
                regx = regex.RegEx(self.alphabet, regex_string)  # create a regex instance for each token
                self.dfa_tokens[name] = regx
        current_file.close()

        with open(source_file, "r") as source:
            self.values = deque()
            source_line = source.readline().strip()

            while source_line: #take each line, split it, and then append value to self.values
                split = source_line.split()
                for value in split:
                    self.values.append(value)
                source_line = source.readline().strip()
        source.close()
        
    def next_token(self):
        """
        Returns the next token from the source_file.
        The token is returned as a tuple with 2 items:
        the first item is the name of the token type (a string),
        and the second item is the specific value of the token (also
        as a string).
        Raises EOFError exception if there are not more tokens in the
        file.
        Raises InvalidToken exception if a valid token cannot be identified,
        but there are characters remaining in the source file.
        """
        if not self.values:
            raise EOFError

        token = self.values.popleft()
        valid_token = [None] * len(token)

        # checking if token doesnt have any invalid characters
        if not all(char in self.alphabet for char in token):
            raise InvalidToken

        # Check if each substring is a valid token
        for i, _ in enumerate(token):
            substring = token[:i + 1]
            for key, regex in self.dfa_tokens.items():
                if regex.simulate(substring):
                    valid_token[i] = key
                    break

        # Find the longest valid substring from the end, faster than searching from the beginning
        for i in reversed(range(len(valid_token))):
            if valid_token[i] is not None:
                split_index = i + 1
                valid_tokens, invalid_tokens = token[:split_index], token[split_index:]
                if invalid_tokens:
                    self.values.appendleft(invalid_tokens)
                return valid_token[i], valid_tokens
        raise InvalidToken("No valid token found.")

if __name__ == "__main__":
    num = 1   # can replace this with any number 1, ... 20.
              # can also create your own test files.
    reg_ex_filename = f"regex{num}.txt" 
    source_filename = f"src{num}.txt"
    lex = Lex(reg_ex_filename, source_filename)
    try:
        while True:
            token = lex.next_token()
            print(token)

    except EOFError:
        pass
    except InvalidToken:
        print("Invalid token")