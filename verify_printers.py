from src.compiler_driver import CompilerDriver
from src.printers import ASTPrinter, IRPrinter, TokenPrinter


SOURCE = """
x = 1
y = 2
if x < y:
    print(x + y)
else:
    print(-y)
"""


def main():
    driver = CompilerDriver()
    tokens = driver.lex(SOURCE)
    ast = driver.parse(tokens)
    ir = driver.build_ir(ast)

    token_printer = TokenPrinter()
    ast_printer = ASTPrinter()
    ir_printer = IRPrinter()

    print("=== TOKENS ===")
    print(token_printer.format_tokens(tokens))
    print()

    print("=== AST ===")
    print(ast_printer.format(ast))
    print()

    print("=== IR ===")
    print(ir_printer.format(ir))


if __name__ == "__main__":
    main()
