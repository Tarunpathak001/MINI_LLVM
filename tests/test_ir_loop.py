import unittest
import sys
import os


from src.lexer import Lexer
from src.parser import Parser
from src.ast_nodes import *
from src.ir_builder import IRBuilder
from src.ir import *

class TestIRLoop(unittest.TestCase):
    def build_ir(self, source):
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        builder = IRBuilder()
        return builder.generate(ast)

    def test_simple_while_structure(self):
        """
        x = 0
        while x < 5:
            x = x + 1
        """
        src = """
x = 0
while x < 5:
    x = x + 1
"""
        ir = self.build_ir(src)
        instrs = ir.instructions
        
        # Verify Labels
        labels = [i for i in instrs if isinstance(i, Label)]
        # Expect: ... (maybe implicit entry), L_while_header, L_while_body, L_while_exit
        label_names = [l.name for l in labels]
        self.assertTrue(any("while_header" in l for l in label_names))
        self.assertTrue(any("while_body" in l for l in label_names))
        self.assertTrue(any("while_exit" in l for l in label_names))

        # Verify Phi in Header
        # Find index of header label
        header_idx = -1
        for idx, i in enumerate(instrs):
            if isinstance(i, Label) and "while_header" in i.name:
                header_idx = idx
                break
        
        self.assertNotEqual(header_idx, -1)
        
        # Instruction immediately after header should be Phi (or close to it)
        # x is defined before (x=0), so x must have a Phi.
        phi_found = False
        for i in range(header_idx + 1, len(instrs)):
            if isinstance(instrs[i], Phi):
                if instrs[i].target.startswith('x_'):
                    phi_found = True
                    # Check inputs: should have 2
                    self.assertEqual(len(instrs[i].inputs), 2)
                    break
            if isinstance(instrs[i], Label): # Stop if we hit next label
                break
                
        self.assertTrue(phi_found, "Phi node for x not found in header")

    def test_backedge_jump(self):
        """Verify body jumps back to header"""
        src = """
x = 0
while x < 5:
    x = x + 1
"""
        ir = self.build_ir(src)
        instrs = ir.instructions
        
        # Find jump at end of body
        # Should be Jump to header
        jumps = [i for i in instrs if isinstance(i, Jump)]
        # We expect at least one jump to header
        jump_to_header = False
        for j in jumps:
            if "while_header" in j.target_label:
                jump_to_header = True
                break
        self.assertTrue(jump_to_header)

    def test_nested_while(self):
        """
        while x:
            while y:
                y = 0
        """
        src = """
x = 1
y = 1
while x:
    while y:
        y = 0
"""
        ir = self.build_ir(src)
        instrs = ir.instructions
        
        # Should have 2 sets of loop labels
        labels = [l.name for l in instrs if isinstance(l, Label)]
        headers = [l for l in labels if "while_header" in l]
        self.assertEqual(len(headers), 2)
        
if __name__ == '__main__':
    unittest.main()