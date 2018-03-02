from grammar import Grammar
from lrClosureTable import LRClosureTable
from lalrTable import LALRTable

text = "Z -> E\n" + "E -> E * E\n" + "E -> E + E\n" + "E -> B\n" + "B -> 0\n" + "B -> 1\n" + "B -> L\n" + "B -> ''\n"
grammar = Grammar(text)
print(str(grammar))
lr_closure_table = LRClosureTable(grammar)
print(str(lr_closure_table))
lalrTable = LALRTable(lr_closure_table)
print(str(lalrTable))
text = "1 + 0 * 1"
_, printed_value = lalrTable.parse(text)
print("---------------AST---------------")
print(printed_value.get_text())