from typing import Dict, List, Optional, Set, Tuple, Union, Callable
from .parser import Parser, CaretNode, DollarNode, DotNode, CharClassNode, ASTNode
from .lexer import Lexer
from .nfa import NFA, State, NFACompiler

class Match:
    """
    Match object returned by regex matching functions.
    Contains information about the match and captured groups.
    """
    def __init__(self, string: str, groups: Dict[int, Tuple[int, int]]) -> None:
        self._string = string
        self._groups = groups

    def group(self, index: int = 0) -> Optional[str]:
        if index not in self._groups:
            return None
        start, end = self._groups[index]
        if start == -1 or end == -1:
            return None
        return self._string[start:end]

    def groups(self) -> Tuple[Optional[str], ...]:
        result = []
        max_idx = max(self._groups.keys()) if self._groups else 0
        for i in range(1, max_idx + 1):
            result.append(self.group(i))
        return tuple(result)

    def start(self, index: int = 0) -> int:
        return self._groups.get(index, (-1, -1))[0]

    def end(self, index: int = 0) -> int:
        return self._groups.get(index, (-1, -1))[1]

    def span(self, index: int = 0) -> Tuple[int, int]:
        return self._groups.get(index, (-1, -1))

    def __repr__(self) -> str:
        return f"<Match object; span={self.span()}, match='{self.group()}'>"

class NFASimulator:
    """
    Simulates an NFA to find matches in a string.
    """
    def __init__(self, nfa: NFA) -> None:
        self.nfa = nfa

    def match(self, string: str, start_pos: int = 0) -> Optional[Match]:
        """
        Tries to match the pattern at the beginning of the string (from start_pos).
        """
        return self._run(string, start_pos)

    def search(self, string: str, start_pos: int = 0) -> Optional[Match]:
        """
        Scans through the string for the first match.
        """
        for i in range(start_pos, len(string) + 1):
            result = self._run(string, i)
            if result:
                return result
        return None

    def findall(self, string: str) -> List[Union[str, Tuple[str, ...]]]:
        """
        Finds all non-overlapping matches.
        """
        results = []
        pos = 0
        while pos <= len(string):
            match_obj = self.search(string, pos)
            if not match_obj:
                break

            # If groups are present, return them as tuple (excluding group 0)
            groups = match_obj.groups()
            if groups:
                if len(groups) == 1:
                    results.append(groups[0] or "")
                else:
                    results.append(tuple(g or "" for g in groups))
            else:
                results.append(match_obj.group(0) or "")

            new_pos = match_obj.end(0)
            if new_pos == pos: # Handle empty matches
                pos += 1
            else:
                pos = new_pos
        return results

    def sub(self, repl: Union[str, Callable[[Match], str]], string: str, count: int = 0) -> str:
        """
        Replaces matches with repl.
        """
        result = []
        pos = 0
        subs_made = 0
        while pos <= len(string):
            if count > 0 and subs_made >= count:
                break

            match_obj = self.search(string, pos)
            if not match_obj:
                break

            result.append(string[pos:match_obj.start(0)])
            if callable(repl):
                result.append(repl(match_obj))
            else:
                # Handle \1, \2 etc in replacement string
                # This is a bit complex for a simple sub, but let's do a basic version.
                replaced = repl
                for i in range(1, 10):
                    if f"\\{i}" in replaced:
                        replaced = replaced.replace(f"\\{i}", match_obj.group(i) or "")
                result.append(replaced)

            pos = match_obj.end(0)
            subs_made += 1
            if match_obj.start(0) == match_obj.end(0): # Empty match
                if pos < len(string):
                    result.append(string[pos])
                    pos += 1
                else:
                    break

        result.append(string[pos:])
        return "".join(result)

    def _run(self, string: str, start_pos: int) -> Optional[Match]:
        initial_groups = {0: (start_pos, -1)}
        active_paths = self._epsilon_closure([(self.nfa.start_state, initial_groups)], string, start_pos)

        best_match_groups = None

        pos = start_pos
        while True:
            # Check for matches in current paths
            # We want the longest match (greedy).
            for state, groups in active_paths:
                if state == self.nfa.end_state:
                    final_groups = groups.copy()
                    final_groups[0] = (start_pos, pos)
                    # For a single starting position, we prefer the longest match.
                    # Since we are iterating pos, the latest one we find that matches will be the longest so far.
                    best_match_groups = final_groups

            if pos >= len(string) or not active_paths:
                break

            char = string[pos]
            next_step_paths = []

            for state, groups in active_paths:
                for transition_val, next_state in state.transitions:
                    if transition_val is None: continue

                    matched = False
                    if isinstance(transition_val, str):
                        if transition_val == char: matched = True
                    elif isinstance(transition_val, DotNode):
                        if char != '\n': matched = True
                    elif isinstance(transition_val, CharClassNode):
                        if self._match_char_class(char, transition_val): matched = True

                    if matched:
                        next_step_paths.append((next_state, groups.copy()))

            if not next_step_paths:
                break

            pos += 1
            active_paths = self._epsilon_closure(next_step_paths, string, pos)

        if best_match_groups:
            return Match(string, best_match_groups)
        return None

    def _epsilon_closure(self, paths: List[Tuple[State, Dict[int, Tuple[int, int]]]], string: str, pos: int) -> List[Tuple[State, Dict[int, Tuple[int, int]]]]:
        closure = []
        stack = list(paths)
        seen = set()

        while stack:
            state, groups = stack.pop()

            # Apply save markers at this state
            new_groups = groups.copy()
            for group_idx, is_start in state.save_markers:
                if is_start:
                    new_groups[group_idx] = (pos, -1)
                else:
                    new_groups[group_idx] = (new_groups.get(group_idx, (-1, -1))[0], pos)

            state_key = (id(state), tuple(sorted(new_groups.items())))
            if state_key in seen:
                continue
            seen.add(state_key)

            closure.append((state, new_groups))

            for transition_val, next_state in state.transitions:
                if transition_val is None:
                    stack.append((next_state, new_groups))
                elif isinstance(transition_val, CaretNode):
                    if pos == 0:
                        stack.append((next_state, new_groups))
                elif isinstance(transition_val, DollarNode):
                    if pos == len(string):
                        stack.append((next_state, new_groups))

        return closure

    def _match_char_class(self, char: str, node: CharClassNode) -> bool:
        matched = False
        if node.special == 'd':
            matched = char.isdigit()
        elif node.special == 'w':
            matched = char.isalnum() or char == '_'
        elif node.special == 's':
            matched = char.isspace()
        else:
            if char in node.chars:
                matched = True
            else:
                for start, end in node.ranges:
                    if start <= char <= end:
                        matched = True
                        break

        return not matched if node.negated else matched

def compile(pattern: str) -> NFASimulator:
    lexer = Lexer(pattern)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = NFACompiler()
    nfa = compiler.compile(ast)
    return NFASimulator(nfa)
