class TokenPrinter:
    """Render lexer tokens in a compact human-readable form."""

    def format_token(self, token):
        if token.value is None:
            return token.type
        return f"{token.type}({repr(token.value)})"

    def format_tokens(self, tokens):
        return "\n".join(self.format_token(token) for token in tokens)
