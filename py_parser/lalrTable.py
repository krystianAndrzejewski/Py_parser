from lrClosureTable import LRClosureTable
from _collections import deque
from grammar import Grammar
from collections import defaultdict
from sortedcontainers import SortedSet

class LALRTable:

    def __init__(self, closure_table):
        self.states = {}
        self.terminals = closure_table.grammar.terminals
        self.nonterminals = closure_table.grammar.nonterminals
        self.rule_length = {}
        for rule in closure_table.grammar.rules:
            self.rule_length[rule.index] = len(rule.igredients)
        self.start_state_index = 0
        for _, kernel in closure_table.kernels.items():
            state = State(kernel.index)
            self.states[state.index] = state
            state.actions['$'] = ErrorAction()
            for terminal in self.terminals:
                state.actions[terminal] = ErrorAction()
            for nonterminal in self.nonterminals:
                state.actions[nonterminal] = ErrorAction()
            for symbol, goto_element in kernel.gotos.items():
                if symbol in self.terminals:
                    state.actions[symbol] = ShiftAction(goto_element.index)
                else:
                    state.actions[symbol] = GotoAction(goto_element.index)
            for item in kernel.closure:
                if item.dot_index == len(item.rule.igredients) or (len(item.rule.igredients) == 1 and item.rule.igredients[0] == Grammar.epsilon):
                    for lookahead in item.lookaheads:
                        action = ReductionAction(item.rule.index, item.rule.product)
                        if state.actions[lookahead].is_error():
                            state.actions[lookahead] = action
                        elif state.actions[lookahead].is_reduction():
                            if state.actions[lookahead].get_reduction_rule() != action.get_reduction_rule():
                                state.rr_conflicts[lookahead].add(action)
                                if(state.actions[lookahead].get_reduction_rule() > action.get_reduction_rule()):
                                    state.actions[lookahead] = action
                        else:
                            state.sr_conflicts[lookahead].add(action)
        for _, state in self.states.items():
            if state.actions['$'].is_reduction() and state.actions['$'].get_reduction_rule() == 0:
                state.actions['$'] = AcceptAction()

    def parse(self, text):
        state_stack = []
        element_tree_stack = []
        is_end = False
        actual_state = self.states[self.start_state_index]
        words = text.split()
        index = 0
        token = words[index]
        state_stack.append(actual_state.index)
        if token not in actual_state.actions:
            return False, None
        action = actual_state.actions[token]
        while not is_end:
            if action.is_shift():
                element_tree_stack.append(ElementTree(words[index], None))
                state_stack.append(action.get_next_state())
                index += 1
            elif action.is_reduction():
                rule_index = action.get_reduction_rule()
                igredients_length = self.rule_length[rule_index]
                taken_tree_elements = [element_tree_stack.pop() for number in range(igredients_length)]
                taken_states = [state_stack.pop() for number in range(igredients_length)]
                new_node = ElementTree(action.nonterminal, *taken_tree_elements)
                element_tree_stack.append(new_node)
            else:
                state_stack.append(action.get_next_state())
            actual_state = self.states[state_stack[-1]]
            if (len(state_stack) + len(element_tree_stack)) % 2 == 1:
                if len(words) > index:
                    token = words[index]
                else:
                    token = '$'
            else:
                token = element_tree_stack[-1].aphabet_element
            if token not in actual_state.actions:
                return False, None
            action = actual_state.actions[token]
            is_end = action.is_error() or action.is_accept()
        returned_element = None
        if len(element_tree_stack) > 0:
            returned_element = element_tree_stack[-1]
        return action.is_accept(), returned_element

    def __str__(self):
        result = "---------------TABLE---------------\n"
        result += 5 * ' ' + '|' + '|'.join("{:>5}".format(terminal) for terminal in self.terminals) + '|' + '|'.join("{:>5}".format(nonterminal) for nonterminal in self.nonterminals) + '|' + 4 * ' ' + '$\n'
        for _, state in self.states.items():
            result += "{:>4}.".format(str(state.index ))
            result += '|' + '|'.join("{:>5}".format(str(state.actions[terminal])) for terminal in self.terminals)
            result += '|' + '|'.join("{:>5}".format(str(state.actions[noterminal])) for noterminal in self.nonterminals)
            result += '|' + "{:>5}".format(str(state.actions['$'])) + '\n'
        return result

class ElementTree:

    def __init__(self, alphabet_element, *childreen):
        self.childreen = []
        if None not in childreen:
            self.childreen = childreen
        self.aphabet_element = alphabet_element

    def get_text(self, intend = ''):
        result = intend + self.aphabet_element + '\n'
        intend += ' ' * 2
        for child in self.childreen:
            result += child.get_text(intend)
        return result

class State:

    def __init__(self, index):
        self.index = index
        self.actions = {}
        self.rr_conflicts = defaultdict(set)
        self.sr_conflicts = defaultdict(set)

class LALRAction:

    def __init__(self):
        pass

    def is_error(self):
        return False

    def is_shift(self):
        return False

    def is_reduction(self):
        return False

    def is_goto(self):
        return True

    def is_accept(self):
        return False

    def get_next_state(self):
        pass

    def get_reduction_rule(self):
        pass

    def get_nonterminal_from_reduction(self):
        pass

    def __str__(self):
        return ''


class ErrorAction(LALRAction):

    def __init__(self):
        pass

    def is_error(self):
        return True

    def __str__(self):
        return ''

class ShiftAction(LALRAction):

    def __init__(self, next_state):
        self.next_state = next_state

    def get_next_state(self):
        return self.next_state

    def is_shift(self):
        return True

    def __str__(self):
        return 's' + str(self.next_state)

class GotoAction(LALRAction):

    def __init__(self, next_state):
        self.next_state = next_state

    def is_goto(self):
        return True

    def get_next_state(self):
        return self.next_state

    def __str__(self):
        return str(self.next_state)

class AcceptAction(LALRAction):

    def __init__(self):
        pass

    def is_accept(self):
        return True

    def __str__(self):
        return 'acc'

class ReductionAction(LALRAction):

    def __init__(self, reduction_rule, nonterminal):
        self.reduction_rule = reduction_rule
        self.nonterminal = nonterminal

    def is_reduction(self):
        return True

    def get_reduction_rule(self):
        return self.reduction_rule

    def get_nonterminal_from_reduction(self):
        return self.nonterminal

    def __str__(self):
        return 'r' + str(self.reduction_rule)