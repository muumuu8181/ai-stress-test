from typing import Dict, List, Optional, Set, Union, Tuple
from .parser import ASTNode, LiteralNode, DotNode, CaretNode, DollarNode, QuantifierNode, CharClassNode, GroupNode, AlternationNode, ConcatenationNode

class State:
    """Represents a state in the NFA."""
    def __init__(self) -> None:
        self.transitions: List[Tuple[Optional[Union[str, CharClassNode, CaretNode, DollarNode, DotNode]], 'State']] = []
        self.save_markers: List[Tuple[int, bool]] = []

    def add_transition(self, char: Optional[Union[str, CharClassNode, CaretNode, DollarNode, DotNode]], state: 'State') -> None:
        self.transitions.append((char, state))

    def add_save_marker(self, group_index: int, is_start: bool) -> None:
        self.save_markers.append((group_index, is_start))

class NFA:
    """Represents a Non-deterministic Finite Automaton fragment."""
    def __init__(self, start_state: State, end_state: State) -> None:
        self.start_state = start_state
        self.end_state = end_state

class NFACompiler:
    """
    Compiles an AST into an NFA using Thompson's construction.
    """
    def compile(self, node: ASTNode) -> NFA:
        if isinstance(node, LiteralNode):
            start = State()
            end = State()
            if node.char == "":
                # Handle empty string matching (epsilon transition)
                start.add_transition(None, end)
            else:
                start.add_transition(node.char, end)
            return NFA(start, end)

        elif isinstance(node, DotNode):
            start = State()
            end = State()
            start.add_transition(DotNode(), end) # Use node itself as marker
            return NFA(start, end)

        elif isinstance(node, CaretNode):
            start = State()
            end = State()
            start.add_transition(CaretNode(), end)
            return NFA(start, end)

        elif isinstance(node, DollarNode):
            start = State()
            end = State()
            start.add_transition(DollarNode(), end)
            return NFA(start, end)

        elif isinstance(node, CharClassNode):
            start = State()
            end = State()
            start.add_transition(node, end)
            return NFA(start, end)

        elif isinstance(node, ConcatenationNode):
            if not node.nodes:
                s = State()
                return NFA(s, s)

            nfas = [self.compile(n) for n in node.nodes]
            for i in range(len(nfas) - 1):
                nfas[i].end_state.add_transition(None, nfas[i+1].start_state)
            return NFA(nfas[0].start_state, nfas[-1].end_state)

        elif isinstance(node, AlternationNode):
            start = State()
            end = State()
            for n in node.nodes:
                fragment = self.compile(n)
                start.add_transition(None, fragment.start_state)
                fragment.end_state.add_transition(None, end)
            return NFA(start, end)

        elif isinstance(node, QuantifierNode):
            return self._compile_quantifier(node)

        elif isinstance(node, GroupNode):
            fragment = self.compile(node.node)
            start = State()
            end = State()
            start.add_save_marker(node.group_index, True)
            start.add_transition(None, fragment.start_state)
            fragment.end_state.add_transition(None, end)
            end.add_save_marker(node.group_index, False)
            return NFA(start, end)

        raise ValueError(f"Unknown AST node type: {type(node)}")

    def _compile_quantifier(self, node: QuantifierNode) -> NFA:
        fragment = self.compile(node.node)

        if node.min_count == 0 and node.max_count is None: # *
            start = State()
            end = State()
            start.add_transition(None, fragment.start_state)
            start.add_transition(None, end)
            fragment.end_state.add_transition(None, fragment.start_state)
            fragment.end_state.add_transition(None, end)
            return NFA(start, end)

        elif node.min_count == 1 and node.max_count is None: # +
            start = State()
            end = State()
            start.add_transition(None, fragment.start_state)
            fragment.end_state.add_transition(None, fragment.start_state)
            fragment.end_state.add_transition(None, end)
            return NFA(start, end)

        elif node.min_count == 0 and node.max_count == 1: # ?
            start = State()
            end = State()
            start.add_transition(None, fragment.start_state)
            start.add_transition(None, end)
            fragment.end_state.add_transition(None, end)
            return NFA(start, end)

        else: # {n, m}
            return self._compile_brace_quantifier(node)

    def _compile_brace_quantifier(self, node: QuantifierNode) -> NFA:
        # For simplicity, we'll repeat the fragments.
        # This can lead to state explosion, but it's correct Thompson-style.
        # min_count copies followed by (max_count - min_count) optional copies.

        def clone_ast(n: ASTNode) -> ASTNode:
            # Simple way to re-compile the same sub-AST multiple times
            return n

        nfas = []
        for _ in range(node.min_count):
            nfas.append(self.compile(clone_ast(node.node)))

        if node.max_count is None:
            # {n,} -> n copies followed by +
            star_fragment = self.compile(clone_ast(node.node))
            s = State()
            e = State()
            s.add_transition(None, star_fragment.start_state)
            star_fragment.end_state.add_transition(None, star_fragment.start_state)
            star_fragment.end_state.add_transition(None, e)
            nfas.append(NFA(s, e))
        else:
            for _ in range(node.max_count - node.min_count):
                opt_fragment = self.compile(clone_ast(node.node))
                s = State()
                e = State()
                s.add_transition(None, opt_fragment.start_state)
                s.add_transition(None, e)
                opt_fragment.end_state.add_transition(None, e)
                nfas.append(NFA(s, e))

        if not nfas:
            s = State()
            return NFA(s, s)

        for i in range(len(nfas) - 1):
            nfas[i].end_state.add_transition(None, nfas[i+1].start_state)

        return NFA(nfas[0].start_state, nfas[-1].end_state)
