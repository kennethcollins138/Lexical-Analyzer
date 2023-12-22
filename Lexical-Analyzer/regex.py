from dfa import DFA
from nfa import NFA
from ast_regex import SymbolLeaf, EpsilonLeaf, EmptyLeaf, ConcatInt, UnionInt, StarInt
from collections import deque

class InvalidExpression(Exception):
    pass

class RegEx:
    def __init__(self, alphabet, regex_string):
        """
        Initializes a regular expression from the file "filename".
        """
        # STAR, CONCAT, UNION, PAREN in order of precedence
        self.OPERATORS = ['*', '&', '|', '(']
        self.operand_stack = []
        self.operator_stack = []
        self.alphabet = alphabet
        # Read the regular expression line from the file
        reg_expr = deque(regex_string[regex_string.find('"') + 1: regex_string.rfind('"')])
        self.epsilon_alphabet = self.alphabet + ['e']

        try:
            while reg_expr:
                char = reg_expr.popleft()
                is_open_parenthesis = char == '('
                is_backslash = char == '\\'
                escaped = is_backslash and reg_expr and len(reg_expr) > 0 and reg_expr[0] == '*'
                if is_backslash:
                    char = reg_expr.popleft()
                    escaped = True
                is_epsilon_alphabet = reg_expr and (reg_expr[0] in self.epsilon_alphabet or reg_expr[0] in ('(', '\\'))

                if is_open_parenthesis:
                    self.operator_stack.append(char)
                else:
                    is_operator_condition = char in self.OPERATORS and not escaped
                    is_close_parenthesis = char == ')' and not escaped
                    is_epsilon_condition = is_epsilon_alphabet and (char not in self.OPERATORS[1:] or escaped) and (reg_expr[0] not in self.OPERATORS[:3])

                    # Handle special cases
                    if is_epsilon_condition and reg_expr[0] != ')':
                        reg_expr.appendleft('&')

                    if is_operator_condition:
                        while self.operator_stack and self.OPERATORS.index(char) >= self.OPERATORS.index(self.operator_stack[-1]):
                            self.operand_stack.append(self.create_interior_node(self.operator_stack.pop()))
                        self.operator_stack.append(char)
                    elif is_close_parenthesis:
                        while self.operator_stack[-1] != '(':
                            self.operand_stack.append(self.create_interior_node(self.operator_stack.pop()))
                        self.operator_stack.pop()
                    elif char in self.epsilon_alphabet or escaped:
                        self.operand_stack.append(self.create_leaf_node(char, escaped))

            if '(' in self.operator_stack:
                raise ValueError("Mismatched parentheses")

            while self.operator_stack:
                self.operand_stack.append(self.create_interior_node(self.operator_stack.pop()))
            
            # Get the root of ast and convert to nfa
            self.root = self.operand_stack.pop()
            self.equiv_nfa = self.to_nfa()
            self.equiv_nfa.alphabet = self.alphabet
            # Convert NFA to DFA
            self.equiv_dfa = self.equiv_nfa.to_DFA()

        except Exception as e:
            raise InvalidExpression(f"Exception: {e}")

    def create_leaf_node(self, char, escaped):
        """
        Creates a leaf ndoe depding on passed char
        """
        if char == "e" and not escaped:
            return EpsilonLeaf(char)
        elif char == 'N' and not escaped:
            return EmptyLeaf(char)
        else:
            return SymbolLeaf(char)

    def create_interior_node(self, char):
        if char == "|":
            right = self.operand_stack.pop()
            left = self.operand_stack.pop()
            return UnionInt(char, left, right)
        elif char == "&":
            right = self.operand_stack.pop()
            left = self.operand_stack.pop()
            return ConcatInt(char, left, right)
        elif char == "*":
            operand = self.operand_stack.pop()
            return StarInt(char, operand)


    def to_nfa(self):
        """
        Returns an NFA object that is equivalent to the regular expression.
        """
        if self.root is not None:
            return self.root.to_nfa()
        return None

    def simulate(self, string):
        """
        Returns True if the string is in the languages defined by the "self" regular expression.
        """
        return self.equiv_dfa.simulate(string)