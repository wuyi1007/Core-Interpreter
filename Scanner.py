from string import whitespace, ascii_letters, digits
from Core import Core

class Scanner:

    def __init__(self, text_stream):
        self.file = open(text_stream, 'r', encoding='ascii')
        self.current_Char = self.file.read(1)

        self.current_Token = None
        self.current_Text = None

        self.currentID = None
        self.currentString = None
        self.currentCONST = None

        # dictionary that mapps keyword strings with corresponding Core enumeration
        self.keywords = {
            "and": Core.AND,
            "begin": Core.BEGIN,
            "case": Core.CASE,
            "do": Core.DO,
            "else": Core.ELSE,
            "end": Core.END,
            "for": Core.FOR,
            "if": Core.IF,
            "in": Core.IN,
            "integer": Core.INTEGER,
            "is": Core.IS,
            "new": Core.NEW,
            "not": Core.NOT,
            "object": Core.OBJECT,
            "or": Core.OR,
            "print": Core.PRINT,
            "procedure": Core.PROCEDURE,
            "read": Core.READ,
            "return": Core.RETURN,
            "then": Core.THEN,
        }

        # dictionary that mapps symbol characters with corresponding Core enumeration
        self.symbols = {
            '+': Core.ADD,
            '-': Core.SUBTRACT,
            '*': Core.MULTIPLY,
            '/': Core.DIVIDE,
            '=': Core.ASSIGN,
            # "==": Core.EQUAL,
            '<': Core.LESS,
            ':': Core.COLON,
            ';': Core.SEMICOLON,
            '.': Core.PERIOD,
            ',': Core.COMMA,
            '(': Core.LPAREN,
            ')': Core.RPAREN,
            '[': Core.LSQUARE,
            ']': Core.RSQUARE,
            '{': Core.LCURL,
            '}': Core.RCURL,
        }
        
        self.nextToken()

    def nextToken(self):
        # Skip whitespace
        while self.current_Char != '' and self.current_Char in whitespace:
            self.current_Char = self.file.read(1)

        # Edge case: End of Stream
        if self.current_Char == '':
            self.current_Token = Core.EOS
            return
        
        # Handle identifiers and keywords
        if self.current_Char in ascii_letters:
            self.current_Text = ''
            # Concatenate string until meeting EOF or non-letter/digit char
            while self.current_Char != '' and self.current_Char in ascii_letters + digits:
                self.current_Text += self.current_Char
                self.current_Char = self.file.read(1)
            # Check if the current_Text is a keyword
            if self.current_Text in self.keywords:
                self.current_Token = self.keywords[self.current_Text]
            # If not a keyword, it's an identifier
            else:
                self.current_Token = Core.ID
                self.currentID = self.current_Text

        # Handle string literals
        elif self.current_Char == "'":
            self.currentString = ""
            # Skip opening quote
            self.current_Char = self.file.read(1)
            # Concatenate string literals until meeting EOF or terminating quote
            while self.current_Char != '' and self.current_Char != "'":
                self.currentString += self.current_Char
                self.current_Char = self.file.read(1)
            # Handle error case: String not terminated
            if self.current_Char == '':
                self.current_Token = Core.ERROR
                print("ERROR: String not terminated")
                return
            # Skip terminating quote
            self.current_Char = self.file.read(1)
            self.current_Token = Core.STRING

        # Handle digits/CONST
        elif self.current_Char in digits:
            self.current_Text = ''
            # Read CONST as String to detect leading 0(s) error case
            while self.current_Char != '' and self.current_Char in digits:
                self.current_Text += self.current_Char
                self.current_Char = self.file.read(1)

            # Handle error case: leading 0(s) in CONST
            if len(self.current_Text) > 1 and self.current_Text[0] == '0':
                self.current_Token = Core.ERROR
                print("ERROR: invalid CONST: " + self.current_Text)
                return

            self.currentCONST = int(self.current_Text)
            # Handle error case: CONST outside boundaries
            if self.currentCONST > 8191:
                self.current_Token = Core.ERROR
                print("ERROR: invalid CONST: " + self.current_Text)
                return
            self.current_Token = Core.CONST

        # Handle valid symbols
        elif self.current_Char in self.symbols:
            self.current_Token = self.symbols[self.current_Char]
            # Hold to store the first symbol for "==" check
            hold = self.current_Char
            # Two purposes: (1 In the case that the symbol is '=', check if the next char is '=' (2 Move reader to the next token
            self.current_Char = self.file.read(1)
            if (hold == '=' and self.current_Char == '='):
                self.current_Token = Core.EQUAL
                self.current_Char = self.file.read(1)
        # Handle error case: invalid symbols
        else:
            print("ERROR: invalid token: " + self.current_Char)
            self.current_Token = Core.ERROR
            return
        

    def currentToken(self):
        return self.current_Token

    def getID(self):
        return self.currentID

    def getString(self):
        return self.currentString

    def getCONST(self):
        return self.currentCONST