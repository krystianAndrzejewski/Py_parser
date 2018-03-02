from collections import deque, defaultdict
from grammar import Grammar
from sortedcontainers import SortedSet

class LRClosureTable:

    def __init__(self, grammar):
        self.grammar = grammar
        self.kernels = {}

        first_kernel = Kernel(0, SortedSet([LALRItem(grammar.root, 0)]), grammar)
        self.kernels[str(first_kernel)] = first_kernel
        lookaheads_propageted = True

        while lookaheads_propageted:
            stack = deque()
            stack.extend([self.kernels[key] for key in self.kernels])
            while len(stack) > 0:
                kernel = stack.pop()
                kernel.compute_closure(grammar)
                new_kernels, cond = self.add_gotos(grammar, kernel)
                stack.extend(new_kernels)
                if(cond):
                    break
            else:
                lookaheads_propageted = False


    def add_gotos(self, grammar, kernel):
        lookaheads_propageted = False
        new_set_lalr_items = defaultdict(SortedSet)
        for closure_item in kernel.closure:
            next_item = closure_item.get_next_item()
            if next_item:
                symbol = closure_item.rule.igredients[closure_item.dot_index]
                new_set_lalr_items[symbol].add(next_item)
                kernel.keys.add(symbol)


        new_kernels = SortedSet()
        for symbol in new_set_lalr_items:
            new_kernel = Kernel(len(self.kernels), new_set_lalr_items[symbol], grammar)
            if str(new_kernel) in self.kernels:
                old_kernel = self.kernels[str(new_kernel)]
                for item in old_kernel.closure:
                    lookaheads_length = len(item.lookaheads)
                    for new_item in new_kernel.closure:
                        item.lookaheads = item.lookaheads.union(new_item.lookaheads)
                    lookaheads_propageted |= lookaheads_length != len(item.lookaheads)
                    new_kernel = old_kernel
            else:
                self.kernels[str(new_kernel)] = new_kernel
                new_kernels.add(new_kernel)
            kernel.gotos[symbol] = new_kernel
        return new_kernels, lookaheads_propageted

    def __str__(self):
        result = "---------------STATES---------------\n"
        return result + '\n'.join("{}".format(self.kernels[key].get_detailed_string()) for key in self.kernels) + ' \n'

class Kernel:

    def __init__(self, index, lr_items, grammar):
        self.index = index
        self.lr_items = lr_items
        self.closure = SortedSet()
        self.closure = self.closure.union(lr_items)
        self.gotos = {}
        self.keys = set()
        self.compute_closure(grammar)

    def compute_closure(self, grammar):
        stack = deque()
        stack.extend(self.closure)
        while len(stack) > 0:
            actualElement = stack.pop()
            new_items = actualElement.get_populated_items(grammar)
            for item in new_items:
                if item not in self.closure:
                    self.closure.add(item)
                    stack.append(item)

    def get_detailed_string(self):
        result = str(self.index) + '. closure { ' + ', '.join("{}".format(str(item)) for item in self.lr_items) + ' } = { ' + ', '.join("{}".format(str(item)) for item in self.closure) + ' }'
        return result

    def __eq__(self, other):
        if other == None or self.lr_items != other.lr_items:
            return False
        return True

    def __str__(self):
        return 'closure { ' + ', '.join("{}".format(super(LALRItem, item).__str__()) for item in self.lr_items) + ' } = { ' + ', '.join("{}".format(super(LALRItem, item).__str__()) for item in self.closure) + ' }'

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other):
        if other == None:
            return False
        return str(self) < str(other)

class BasicLRItem:

    def __init__(self, rule, dot_index):
        self.rule = rule
        self.dot_index = dot_index

    def get_populated_items(self, grammar, created_type_object):
        result = set()
        if self.dot_index < len(self.rule.igredients) and grammar.rules_for_nonterminal[self.rule.igredients[self.dot_index]]:
            for rule in grammar.rules_for_nonterminal[self.rule.igredients[self.dot_index]]:
                result.add(created_type_object(rule, 0))
        return result

    def get_next_item(self, created_type_object):
        if len(self.rule.igredients) <= self.dot_index or (len(self.rule.igredients) == 1 and self.rule.igredients[0] == Grammar.epsilon):
            return None
        else:
            return created_type_object(self.rule, self.dot_index + 1)

    def __str__(self):
        return self.rule.product + ' -> ' + ' '.join(self.rule.igredients[0:self.dot_index]) + '.' + ' '.join(self.rule.igredients[self.dot_index:])

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if other == None:
            return False
        return str(self) == str(other)

class LALRItem(BasicLRItem):

    def __init__(self, rule, dot_index):
        super(LALRItem, self).__init__(rule, dot_index)
        self.lookaheads =  set()
        if rule.index == 0:
            self.lookaheads.add('$')

    def get_populated_items(self, grammar):
        result = super(LALRItem, self).get_populated_items(grammar, LALRItem)
        if len(result) == 0:
            return result
        new_lookaheads, was_empty = grammar.get_first_seq(self.rule, self.dot_index + 1)
        if was_empty:
            new_lookaheads = new_lookaheads.union(self.lookaheads)
        for item in result:
            item.lookaheads = item.lookaheads.union(new_lookaheads)
        return result

    def get_next_item(self):
        result = super(LALRItem, self).get_next_item(LALRItem)
        if result:
            result.lookaheads = result.lookaheads.union(self.lookaheads)
        return result

    def __str__(self):
        return '[ ' + super(LALRItem, self).__str__() + ', ' + '/'.join(self.lookaheads) + ']'

    def __hash__(self):
        return hash(super(LALRItem, self).__str__())

    def __eq__(self, other):
        if other == None:
            return False
        result = super(LALRItem, other).__str__()  == super(LALRItem, self).__str__() 
        if result == True:
            self.lookaheads = self.lookaheads.union(other.lookaheads)
            other.lookaheads = self.lookaheads
        return result

    def __lt__(self, other):
        if other == None:
            return False
        return super(LALRItem, self).__str__() < super(LALRItem, other).__str__()

