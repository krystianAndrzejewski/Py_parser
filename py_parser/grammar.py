from collections import defaultdict 

class Grammar:

    epsilon = "''"

    def __init__(self, text):
        self.alphabet = set()
        self.nonterminals = set()
        self.terminals = set()
        self.rules = set()
        self.root = None
        self.rules_for_nonterminal = defaultdict(set)
        self.initialize_basic_elements(text)
        self.determine_firsts()
        self.determine_follows()

    def initialize_basic_elements(self, text):
        lines = text.split('\n');
        for line in lines:
            if line == '':
                continue
            rule = Rule(line, len(self.rules))
            if self.root == None:
                self.root = rule
            self.rules.add(rule)
            self.rules_for_nonterminal[rule.product].add(rule)
            self.alphabet.add(rule.product)
            self.nonterminals.add(rule.product)
            self.alphabet |= set(rule.igredients)
        self.alphabet -= set(["''"])
        self.terminals = self.alphabet - self.nonterminals

    def determine_firsts(self):
        changed = True
        self.firsts = defaultdict(set)
        while changed == True:
            changed = False
            for rule in self.rules:
                changed |= self.get_first_terminal(rule)

    def determine_follows(self):
        changed = True
        self.follows = defaultdict(set)
        self.follows[self.root.product].add('$')
        while changed == True:
            changed = False
            was_empty = True
            for rule in self.rules:
                if len(rule.igredients) == 0:
                    continue
                for i in range(len(rule.igredients)):
                    was_empty = True
                    if rule.igredients[i] in self.nonterminals:
                        for j in range(i + 1, len(rule.igredients)):
                            if rule.igredients[j] in self.nonterminals:
                                was_empty = False
                                for first_element in self.firsts[rule.igredients[j]]:
                                    if first_element is Grammar.epsilon:
                                        was_empty = True
                                    elif first_element not in self.follows[rule.igredients[i]]:
                                        self.follows[rule.igredients[i]].add(first_element)
                                        changed = True
                                if not was_empty:
                                    break
                            elif rule.igredients[j] in self.terminals:
                                if rule.igredients[j] not in self.follows[rule.igredients[i]]:
                                    self.follows[rule.igredients[i]].add(rule.igredients[j])
                                    changed = True
                                was_empty = False
                                break
                        if was_empty:
                            for follow_element in self.follows[rule.product]:
                                if follow_element not in self.follows[rule.igredients[i]]:
                                    self.follows[rule.igredients[i]].add(follow_element)
                                    changed = True

    def get_first_seq(self, rule, index):
        was_empty = True
        result = set()
        for j in range(index, len(rule.igredients)):
            if rule.igredients[j] in self.nonterminals:
                was_empty = False
                for first_element in self.firsts[rule.igredients[j]]:
                    was_empty |= first_element is Grammar.epsilon
                    if first_element is not Grammar.epsilon:
                        result.add(first_element)
                if not was_empty:
                    break
            elif rule.igredients[j] in self.terminals:
                result.add(rule.igredients[j])
                was_empty = False
                break
        return result, was_empty


    def get_first_terminal(self, rule):
        changed = False
        if len(rule.igredients) == 1 and rule.igredients[0] == Grammar.epsilon:
            if Grammar.epsilon not in self.firsts[rule.product]:
                self.firsts[rule.product].add(Grammar.epsilon)
                changed = True
            return changed
        is_epsilon_present = True
        for igredient in rule.igredients:
            is_epsilon_present = False
            if igredient in self.terminals:
                if igredient not in self.firsts[rule.product]:
                    changed = True
                    self.firsts[rule.product].add(igredient)
            if igredient in self.nonterminals:
                for element in self.firsts[igredient]:
                    is_epsilon_present |= element == Grammar.epsilon
                    if element not in self.firsts[rule.product]:
                        self.firsts[rule.product].add(element)
                        changed = True
        return changed

    def __str__(self):
        result = '-------------------GRAMMAR-------------------\n'
        result += 'Alphabet: ' + ', '.join(self.alphabet) + '\n'
        result += 'Terminals: ' + ', '.join(self.terminals) + '\n'
        result += 'Nonterminals: ' + ', '.join(self.nonterminals) + '\n'
        result += 'Root rule: ' + str(self.root) + '\n'
        result += 'Rules:\n' + '\n'.join("{}. {}".format(rule.index, str(rule)) for rule in self.rules) + '\n'
        result += 'Rules for nonterminals:\n' + '\n'.join("{}:\n{}".format(nonterminal, '\n'.join("{}".format(str(rule)) for rule in self.rules_for_nonterminal[nonterminal])) for nonterminal in self.rules_for_nonterminal) + '\n'
        result += 'First terminals for nonterminals:\n' + '\n'.join("{}: {}".format(nonterminal, ', '.join("{}".format(terminal) for terminal in self.firsts[nonterminal])) for nonterminal in self.firsts) + '\n'
        result += 'Follow terminals for nonterminals:\n' + '\n'.join("{}: {}".format(nonterminal, ', '.join("{}".format(terminal) for terminal in self.follows[nonterminal])) for nonterminal in self.follows) + '\n'
        return result


class Rule:

    def __init__(self, text, index):
        self.index = index
        self.product, self.igredients = text.split('->')
        self.igredients = self.igredients.split(' ')
        self.product = self.product.strip()
        if self.product == '':
            raise RuntimeError("Wrong format of the input string")
        self.igredients = [igredient.strip() for igredient in self.igredients if igredient != '']
        if len(self.igredients) == 0:
            raise RuntimeError("Wrong format of the input string")

    def __eq__(self, otherRule):
        if otherRule == None:
            return False
        if self.product != otherRule.product:
            return False
        if self.igredients != otherRule.igredients:
            return False
        return True

    def __str__(self):
        return self.product + ' -> ' + ' '.join(self.igredients)

    def __hash__(self):
        return hash(str(self))