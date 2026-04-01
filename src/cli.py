import argparse
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

from src.bytecode import Add, Branch as BCBranch, Eq, Gt, Jump as BCJump, Label as BCLabel
from src.bytecode import Load, Lt, Ne, Neg, Print as BCPrint, Push, Store, Sub
from src.compiler_driver import CompilerDriver
from src.printers import ASTPrinter, IRPrinter, TokenPrinter


def read_source(path_str):
    return Path(path_str).read_text(encoding="utf-8")


def format_bytecode_instruction(instr):
    if isinstance(instr, BCLabel):
        return f"{instr.name}:"
    if isinstance(instr, Push):
        return f"  push {repr(instr.value)}"
    if isinstance(instr, Load):
        return f"  load {instr.name}"
    if isinstance(instr, Store):
        return f"  store {instr.name}"
    if isinstance(instr, Add):
        return "  add"
    if isinstance(instr, Sub):
        return "  sub"
    if isinstance(instr, Lt):
        return "  lt"
    if isinstance(instr, Gt):
        return "  gt"
    if isinstance(instr, Eq):
        return "  eq"
    if isinstance(instr, Ne):
        return "  ne"
    if isinstance(instr, Neg):
        return "  neg"
    if isinstance(instr, BCJump):
        return f"  jump {instr.target}"
    if isinstance(instr, BCBranch):
        return f"  branch {instr.true_label} {instr.false_label}"
    if isinstance(instr, BCPrint):
        return "  print"
    return f"  UNKNOWN_BYTECODE({type(instr).__name__})"


def format_bytecode(bytecode):
    return "\n".join(format_bytecode_instruction(instr) for instr in bytecode)


def build_parser():
    parser = argparse.ArgumentParser(prog="mini-llvm", description="Mini-LLVM compiler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("tokens", "ast", "ir", "run", "pipeline"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("file", help="Path to a Mini-Python source file")

    return parser


def run_tokens(source):
    driver = CompilerDriver()
    return TokenPrinter().format_tokens(driver.lex(source))


def run_ast(source):
    driver = CompilerDriver()
    tokens = driver.lex(source)
    ast = driver.parse(tokens)
    return ASTPrinter().format(ast)


def run_ir(source):
    driver = CompilerDriver()
    result = driver.compile(source)
    return IRPrinter().format(result["optimized_ir"])


def run_program(source):
    driver = CompilerDriver()
    driver.run(source)
    return None


def run_pipeline(source):
    driver = CompilerDriver()
    result = driver.compile(source)

    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        driver.execute(result["bytecode"])

    sections = [
        ("SOURCE", source.rstrip()),
        ("TOKENS", TokenPrinter().format_tokens(result["tokens"])),
        ("AST", ASTPrinter().format(result["ast"])),
        ("IR", IRPrinter().format(result["optimized_ir"])),
        ("BYTECODE", format_bytecode(result["bytecode"])),
        ("OUTPUT", output_buffer.getvalue().rstrip()),
    ]

    rendered = []
    for title, body in sections:
        rendered.append(f"--- {title} ---")
        rendered.append(body)
    return "\n\n".join(rendered)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        source = read_source(args.file)

        if args.command == "tokens":
            output = run_tokens(source)
        elif args.command == "ast":
            output = run_ast(source)
        elif args.command == "ir":
            output = run_ir(source)
        elif args.command == "run":
            output = run_program(source)
        elif args.command == "pipeline":
            output = run_pipeline(source)
        else:
            parser.error(f"Unknown command: {args.command}")
            return 2

        if output:
            print(output)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
