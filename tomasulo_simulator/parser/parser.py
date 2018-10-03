from lark import Lark
from pkg_resources import resource_string

from ..instruction import HaltInstruction
from ..instruction import Label
from ..instruction.bitwise_instructions import AndInstruction, OrInstruction
from ..instruction import (
    BEQInstruction, BNEInstruction,
    BLTInstruction, BLEInstruction,
    BGTInstruction, BGEInstruction,
    JumpInstruction
)
from ..instruction.floating_instructions import FAddInstruction, FSubInstruction
from ..instruction.integer_instructions import AddInstruction, SubInstruction
from ..instruction.logic_instructions import AndlInstruction, OrlInstruction
from ..instruction import LoadInstruction, StoreInstruction

grammar = resource_string("tomasulo_simulator.parser", "grammar.lark").decode("utf-8")


class Parser:
    def __init__(self):
        self.constants = {}

    def parse_code(self, string):
        parser = Lark(grammar, parser="lalr")
        ast = parser.parse(string)
        directives = self.ast_to_directives(list(ast.find_data("directives"))[0].children)
        instructions = self.ast_to_instructions(ast)
        return directives, instructions

    def parse_instruction(self, instruction):
        if instruction.data == "alu_instruction":
            operation = self.get_alu_op(instruction)
            dst = self.get_dst(instruction)
            op1 = self.get_op1(instruction)
            op2 = self.get_op2(instruction)
            if operation == "ADD":
                return AddInstruction(dst, op1, op2)
            elif operation == "SUB":
                return SubInstruction(dst, op1, op2)
            elif operation == "AND":
                return AndInstruction(dst, op1, op2)
            elif operation == "OR":
                return OrInstruction(dst, op1, op2)
            elif operation == "ANDL":
                return AndlInstruction(dst, op1, op2)
            elif operation == "ORL":
                return OrlInstruction(dst, op1, op2)
        if instruction.data == "fp_alu_instruction":
            operation = self.get_fp_alu_op(instruction)
            dst = self.get_fp_dst(instruction)
            op1 = self.get_fp_op1(instruction)
            op2 = self.get_fp_op2(instruction)
            if operation == "FADD":
                return FAddInstruction(dst, op1, op2)
            elif operation == "FSUB":
                return FSubInstruction(dst, op1, op2)
        elif instruction.data == "jump_instruction":
            label = self.get_label(instruction)
            return JumpInstruction(label)
        elif instruction.data == "branch_instruction":
            branch_op = self.get_branch_op(instruction)
            op1 = self.get_op1(instruction)
            op2 = self.get_op2(instruction)
            label = self.get_label(instruction)
            if branch_op == "BEQ":
                return BEQInstruction(op1, op2, label)
            elif branch_op == "BNE":
                return BNEInstruction(op1, op2, label)
            elif branch_op == "BLT":
                return BLTInstruction(op1, op2, label)
            elif branch_op == "BLE":
                return BLEInstruction(op1, op2, label)
            elif branch_op == "BGT":
                return BGTInstruction(op1, op2, label)
            elif branch_op == "BGE":
                return BGEInstruction(op1, op2, label)
        elif instruction.data == "load_instruction":
            dst = self.get_dst(instruction)
            offset_reg = self.get_register(instruction)
            if offset_reg is None:
                offset_reg = "R0"
            base = self.get_immediate(instruction)
            return LoadInstruction(dst, offset_reg, base)
        elif instruction.data == "store_instruction":
            src = self.get_src(instruction)
            offset_reg = self.get_register(instruction)
            if offset_reg is None:
                offset_reg = "R0"
            base = self.get_immediate(instruction)
            return StoreInstruction(src, offset_reg, base)
        elif instruction.data == "halt_instruction":
            return HaltInstruction()
        elif instruction.data == "label_declaration":
            label = instruction.children[0]
            return Label(label)
        elif instruction.data == "const_declaration":
            name = instruction.children[0]
            val = int(instruction.children[1])
            self.constants[name] = val
        else:
            raise Exception("Unrecognized instruction: {}".format(instruction.data))

    @staticmethod
    def ast_to_directives(ast):
        directives = {}
        for directive in ast:
            directives[directive.children[0].lstrip(".")] = int(directive.children[1])
        return directives

    def ast_to_instructions(self, ast):
        instructions = list(ast.find_data("instructions"))[0].children
        return [self.parse_instruction(i) for i in instructions]

    @staticmethod
    def get_first_child(tree, child_name, upper=False):
        try:
            data = tree.find_data(child_name).__next__().children[0]
            if isinstance(data, str) and upper:
                return data.upper()
            else:
                return data
        except StopIteration:
            return None

    def get_alu_op(self, instruction):
        return self.get_first_child(instruction, "alu_op", upper=True)

    def get_dst(self, instruction):
        return self.get_first_child(instruction, "dst_register", upper=True)

    def get_src(self, instruction):
        return self.get_first_child(instruction, "src_register", upper=True).upper()

    def get_immediate(self, instruction):
        immediate = self.get_first_child(instruction, "immediate")
        if immediate in self.constants:
            return self.constants[immediate]
        else:
            return int(immediate)

    def get_register(self, instruction):
        return self.get_first_child(instruction, "register", upper=True)

    def get_op1(self, instruction):
        operand = self.get_first_child(instruction, "operand1", upper=True)
        if operand in self.constants:
            return self.constants[operand]

        try:
            return int(operand)
        except ValueError:
            return operand

    def get_op2(self, instruction):
        operand = self.get_first_child(instruction, "operand2", upper=True)
        if operand in self.constants:
            return self.constants[operand]

        try:
            return int(operand)
        except ValueError:
            return operand

    def get_fp_alu_op(self, instruction):
        return self.get_first_child(instruction, "fp_alu_op", upper=True)

    def get_fp_op1(self, instruction):
        operand = self.get_first_child(instruction, "fp_operand1", upper=True)
        if operand in self.constants:
            return self.constants[operand]

        try:
            return int(operand)
        except ValueError:
            return operand

    def get_fp_op2(self, instruction):
        operand = self.get_first_child(instruction, "fp_operand2", upper=True)
        if operand in self.constants:
            return self.constants[operand]

        try:
            return int(operand)
        except ValueError:
            return operand

    def get_fp_dst(self, instruction):
        return self.get_first_child(instruction, "fp_dst_register", upper=True)

    def get_branch_op(self, instruction):
        return self.get_first_child(instruction, "branch_op", upper=True)

    def get_label(self, instruction):
        return self.get_first_child(instruction, "label")
