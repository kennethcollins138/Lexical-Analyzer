# Name: test_pa4.py
# Author: Dr. Glick
# Date: November 13, 2021
# Description: Tests pa4 for comp 370

from lexer import Lex, InvalidToken

def read_results_file(filename):
    file = open(filename)
    return [True if result == "true" else False for result in file.read().split()]

if __name__ == "__main__":
    num_test_files = 22
    num_correct_tests = 0
    for i in range(1, num_test_files + 1):
        regex_filename = f"regex{i}.txt"
        source_filename = f"src{i}.txt"
        correct_results_filename = f"correct{i}.txt"

        print(f"\nTesting {regex_filename} on source from {source_filename}")
        # Create Lex
        try:
            lex = Lex(regex_filename, source_filename)

            # Read correct file
            correct_file = open(correct_results_filename)
            correct_answers = [line.strip().split() for line in correct_file.readlines()]

            # Make sure lex returns the same tokens
            num_tokens = len(correct_answers)
            num_correct = 0
            i = 0
            while i < num_tokens:
                if correct_answers[i][0] == "INVALID":
                    try:
                        token = lex.next_token()
                        print(f"Token {i}: Incorrect.  Should have raised InvalidToken exception")
                    except InvalidToken:
                        print(f"Token {i}: Correct.  InvalidToken exception raised")
                        num_correct += 1
                else:
                    try:
                        token = lex.next_token()
                        res = "Correct" if token[0] == correct_answers[i][0] and token[1] == correct_answers[i][1] else "Incorrect"
                        print(f"Token {i}: {res}: ", end='')
                        if res == "Correct":
                            print(f"token type = {token[0]}: token value = {token[1]}")
                            num_correct += 1
                        else:
                            print(f"correct token type = {correct_answers[i][0]}: your token type = {token[0]}")
                            print(f"correct token value = {correct_answers[i][1]}: your token value = {token[1]}")
                    except InvalidToken:
                        print(f"Token {i}: Incorrect.  Should not have raised InvalidToken exception")
                i += 1

            if correct_answers[i-1][0] != "INVALID":
                try:
                    token = lex.next_token()
                    print("Your code did not raise an EOFError exception when it should have")
                    print(f"It returned the token {token}")
                    num_correct -= 1
                except EOFError:
                    pass

            if num_correct == num_tokens:
                print("Everything correct for this test")
                num_correct_tests += 1
        
        except EOFError:
            print("Your code raised an EOFError exception before it should have")
    if num_correct_tests == num_test_files:
        print("\nAll tests correct.  Nice job!")
    else:
        print("\nOne or more tests incorrect.  Keep at it.")        
        
