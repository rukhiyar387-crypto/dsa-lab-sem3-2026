import re
# STEP 1: Stack class
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return self.items.copy()


# STEP 2: Tokenizer
def tokenize(expr: str) -> list[str]:
    pattern = r"\d+(?:\.\d+)?|[a-zA-Z_]\w*|[\+\-\*\/\^\%\(\)=]"
    tokens = []
    position = 0

    while position < len(expr):
        if expr[position].isspace():
            position += 1
            continue

        match = re.match(pattern, expr[position:])
        if not match:
            raise ValueError(f"Invalid character: {expr[position]}")

        token = match.group()
        tokens.append(token)
        position += len(token)

    if not tokens:
        raise ValueError("Empty expression")
    return tokens


# STEP 3: Infix-to-postfix conversion
PRECEDENCE = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "%": 2,
    "^": 3,
}
RIGHT_ASSOCIATIVE = {"^"}


def infix_to_postfix(tokens):
    output = []
    stack = Stack()

    for token in tokens:
        if re.fullmatch(r"\d+(?:\.\d+)?|[a-zA-Z_]\w*", token):
            output.append(token)

        elif token == "(":
            stack.push(token)

        elif token == ")":
            while not stack.is_empty() and stack.peek() != "(":
                output.append(stack.pop())

            if stack.is_empty():
                raise ValueError("Mismatched parentheses")

            stack.pop()  # Remove the opening parenthesis

        elif token in PRECEDENCE:
            while not stack.is_empty() and stack.peek() in PRECEDENCE:
                top = stack.peek()

                higher_priority = PRECEDENCE[top] > PRECEDENCE[token]
                equal_and_left = (
                    PRECEDENCE[top] == PRECEDENCE[token]
                    and token not in RIGHT_ASSOCIATIVE
                )

                if higher_priority or equal_and_left:
                    output.append(stack.pop())
                else:
                    break

            stack.push(token)

        else:
            raise ValueError(f"Invalid token: {token}")

    while not stack.is_empty():
        top = stack.pop()
        if top == "(":
            raise ValueError("Mismatched parentheses")
        output.append(top)

    return output


# STEP 4: Postfix evaluator
def eval_postfix(tokens, variables):
    stack = Stack()

    for token in tokens:
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            if "." in token:
                stack.push(float(token))
            else:
                stack.push(int(token))

        elif re.fullmatch(r"[a-zA-Z_]\w*", token):
            if token not in variables:
                raise ValueError(f"Unknown variable: {token}")
            stack.push(variables[token])

        elif token in PRECEDENCE:
            if stack.size() < 2:
                raise ValueError("Invalid expression")

            b = stack.pop()
            a = stack.pop()

            if token == "+":
                result = a + b
            elif token == "-":
                result = a - b
            elif token == "*":
                result = a * b
            elif token == "/":
                if b == 0:
                    raise ZeroDivisionError("Division by zero")
                result = a / b
            elif token == "%":
                if b == 0:
                    raise ZeroDivisionError("Division by zero")
                result = a % b
            elif token == "^":
                result = a ** b

            stack.push(result)

        else:
            raise ValueError(f"Invalid token: {token}")

    if stack.size() != 1:
        raise ValueError("Invalid expression")

    return stack.pop()


# STEP 5: Calculator engine
class PyStackCalc:
    def __init__(self):
        self.variables = {"pi": 3.14159, "e": 2.71828}
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def execute(self, command):
        command = command.strip()

        if not command:
            raise ValueError("Empty command")

        if command.lower() == "undo":
            if self.undo_stack.is_empty():
                raise ValueError("Nothing to undo")
            self.redo_stack.push(dict(self.variables))
            self.variables = self.undo_stack.pop()
            return None

        if command.lower() == "redo":
            if self.redo_stack.is_empty():
                raise ValueError("Nothing to redo")
            self.undo_stack.push(dict(self.variables))
            self.variables = self.redo_stack.pop()
            return None

        assignment = re.fullmatch(
            r"(?:let\s+)?([a-zA-Z_]\w*)\s*=\s*(.+)",
            command,
        )

        if assignment:
            name = assignment.group(1)
            expression = assignment.group(2)

            # Calculate first so a failed assignment changes nothing.
            value = eval_postfix(
                infix_to_postfix(tokenize(expression)),
                self.variables,
            )

            self.undo_stack.push(dict(self.variables))
            self.redo_stack = Stack()
            self.variables[name] = value
            return value

        return eval_postfix(
            infix_to_postfix(tokenize(command)),
            self.variables,
        )

    def start_repl(self):
        print("PyStackCalc - type 'exit' to quit")
        print("Use 'undo' and 'redo' to manage variable changes.")

        while True:
            try:
                command = input("calc> ").strip()

                if command.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break

                result = self.execute(command)

                if result is not None:
                    print(result)
                elif command.lower() not in ("undo", "redo"):
                    print("Done")

            except (ValueError, ZeroDivisionError, IndexError) as error:
                print("Error:", error)


# STEP 6: Automated tests
def run_tests():
    print("Running PyStackCalc Test Suite...")
    engine = PyStackCalc()

    assert engine.execute("3 + 4 * 2") == 11
    assert engine.execute("(3 + 4) * 2") == 14
    assert engine.execute("2 ^ 3 ^ 2") == 512
    assert engine.execute("( 3 + 4 ) * 2 - 8 / 4") == 12

    engine.execute("let x = 15")
    engine.execute("let y = x * 2 - 10")
    assert engine.variables["y"] == 20

    engine.execute("undo")
    assert "y" not in engine.variables

    engine.execute("redo")
    assert engine.variables["y"] == 20

    try:
        engine.execute("(3 + 4 * 2")
        assert False, "Expected ValueError for missing closing parenthesis"
    except ValueError:
        pass

    try:
        engine.execute("100 / (4 - 4)")
        assert False, "Expected ZeroDivisionError"
    except ZeroDivisionError:
        pass

    print("All 9 test cases passed successfully!")


# STEP 7: Choose tests or interactive calculator
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        calc = PyStackCalc()
        calc.start_repl()