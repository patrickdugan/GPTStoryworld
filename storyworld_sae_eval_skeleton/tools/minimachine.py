
# tools/minimachine.py
# Tiny RPN machine with a handful of ops and deterministic execution
from typing import List, Tuple

class MiniMachineError(Exception):
    pass

def run(program: List[str]) -> Tuple[bool, List[int]]:
    stack: List[int] = []
    ip = 0
    prog = program[:]
    try:
        while ip < len(prog):
            tok = prog[ip].upper()
            if tok == "PUSH":
                ip += 1
                stack.append(int(prog[ip]))
            elif tok == "ADD":
                b, a = stack.pop(), stack.pop()
                stack.append(a + b)
            elif tok == "SUB":
                b, a = stack.pop(), stack.pop()
                stack.append(a - b)
            elif tok == "MUL":
                b, a = stack.pop(), stack.pop()
                stack.append(a * b)
            elif tok == "EQ":
                ip += 1
                k = int(prog[ip])
                v = stack.pop()
                stack.append(1 if v == k else 0)
            elif tok == "JMPZ":
                ip += 1
                target = int(prog[ip])
                v = stack.pop()
                if v == 0:
                    ip = target
                    continue
            elif tok == "HALT":
                return True, stack
            else:
                raise MiniMachineError(f"Unknown token: {tok}")
            ip += 1
        return False, stack
    except Exception as e:
        raise MiniMachineError(str(e))
