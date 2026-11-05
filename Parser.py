
from Core import Core
from Scanner import Scanner

class Parser:
    def __init__(self, scanner: Scanner):
        # Provides the token stream for parsing
        self.scanner = scanner
        # Provides semantic analysis
        self.semantic_Checker = None
        # the parse tree root
        self.procedure = None

    # Match the current token with the expected token and advance the scanner
    def match(self, expected_Token, derivation):
        current_Token = self.scanner.currentToken()
        if current_Token == expected_Token:
            self.scanner.nextToken()
        else:
            self.error("Invalid derivation for " + 
                       derivation + ": expected " + 
                       expected_Token.name + 
                       " but found " + 
                       current_Token.name)
    
    # Report a parsing error and exit
    def error(self, error_Message):
        if self.scanner.currentToken() == Core.ERROR:
            raise SystemExit
        print("ERROR: " + error_Message)
        raise SystemExit

    # Start the recursive descent parsing from the procedure (the root of the parse tree)
    def parse(self):
        self.procedure = Procedure()
        self.procedure.parse(self)

    # Perform semantic analysis on the parse tree from the procedure
    def semanticCheck(self):
        self.semantic_Checker = SemanticChecker()
        self.procedure.semanticCheck(self.semantic_Checker)

    # Print the parse tree from the procedure
    def print(self):
        self.procedure.print()

    def execute(self, memory):
        self.procedure.execute(memory)

# <procedure> ::= procedure ID is <decl-seq> begin <stmt-seq> end  | procedure ID is begin <stmt-seq> end
class Procedure:
    def __init__(self):
        # procedure name
        self.name = None
        # statement sequence (StmtSeq class)
        self.ss = None
        # declaration sequence (DecSeq class)
        self.ds = None

    # Parse the procedure
    def parse(self, parser: Parser):
        parser.match(Core.PROCEDURE, "<procedure>")

        # Parse the ID explicitly to obtain the procedure name 
        # (match() advances the scanner, which disables getID())
        if parser.scanner.currentToken() != Core.ID:
            parser.error("Invalid derivation for <procedure>: expected " + 
                         Core.ID.name + 
                         " but found " + 
                         parser.scanner.currentToken().name)
        self.name = parser.scanner.getID()
        parser.scanner.nextToken()

        parser.match(Core.IS, "<procedure>")

        # Derivation alternative: procedure ID is <decl-seq> begin <stmt-seq> end
        # When the next token is not BEGIN, parse the declaration sequence
        if parser.scanner.currentToken() != Core.BEGIN:
            self.ds = DecSeq()
            self.ds.parse(parser)

        parser.match(Core.BEGIN, "<procedure>")

        # Parse the statement sequence
        self.ss = StmtSeq()
        self.ss.parse(parser)

        parser.match(Core.END, "<procedure>")
        parser.match(Core.EOS, "<procedure>")

    # Print the procedure
    def print(self):
        print("procedure " + self.name + " is")
        if self.ds is not None:
            self.ds.print(1)
        print("begin")
        self.ss.print(1)
        print("end")

    # Perform semantic analysis on the procedure
    # Continue semantic analysis on Statement Sequence, and Declaration Sequence when applicable
    def semanticCheck(self, semantic_Checker):
        if self.ds is not None:
            self.ds.semanticCheck(semantic_Checker)
        semantic_Checker.scopes.append({})
        self.ss.semanticCheck(semantic_Checker)
        semantic_Checker.scopes.pop()

    def execute(self, memory):
        if self.ds is not None:
            self.ds.execute(memory)
        memory.enter_scope()
        self.ss.execute(memory)
        memory.exit_scope()

# <decl-seq> ::= <decl> | <decl><decl-seq>
class DecSeq:
    def __init__(self):
        self.decl = None
        self.declSeq = None

    # Parse the declaration sequence
    def parse(self, parser: Parser):
        self.decl = Decl()
        self.decl.parse(parser)

        current_Token = parser.scanner.currentToken()
        # The first set of <decl-seq> is { INTEGER, OBJECT }
        # If the current token is either of these, parse the next declaration sequence
        if current_Token == Core.INTEGER or current_Token == Core.OBJECT:
            self.declSeq = DecSeq()
            self.declSeq.parse(parser)

    # Print the declaration sequence
    def print(self, indent=1):
        self.decl.print(indent)
        if self.declSeq is not None:
            self.declSeq.print(indent)

    # Perform semantic analysis on the declaration, and declaration sequence when applicable
    def semanticCheck(self, semantic_Checker):
        self.decl.semanticCheck(semantic_Checker)
        if self.declSeq is not None:
            self.declSeq.semanticCheck(semantic_Checker)

    def execute(self, memory):
        self.decl.execute(memory)
        if self.declSeq is not None:
            self.declSeq.execute(memory)

# <decl> ::= <decl-integer> | <decl-obj>
class Decl:
    def __init__(self):
        self.decl = None

    # Parse the declaration
    def parse(self, parser: Parser):
        current_Token = parser.scanner.currentToken()
        # The first set of <decl-integer> is { INTEGER }
        if current_Token == Core.INTEGER:
            self.decl = Decl_Integer()
        # The first set of <decl-obj> is { OBJECT }
        elif current_Token == Core.OBJECT:
            self.decl = Decl_Obj()
        # Invalid derivation
        else:
            parser.error("Invalid derivation for <decl>: expected " + 
                         Core.INTEGER.name + 
                         " or " + 
                         Core.OBJECT.name + 
                         " but found " + 
                         current_Token.name)
        self.decl.parse(parser)

    # Print the declaration
    def print(self, indent=1):
        self.decl.print(indent)

    # Perform semantic analysis on the declaration integer or object
    def semanticCheck(self, semantic_Checker):
        self.decl.semanticCheck(semantic_Checker)

    def execute(self, memory):
        self.decl.execute(memory)

# <decl-integer> ::= integer id ;
class Decl_Integer:
    def __init__(self):
        self.integerID = None

    # Parse the declaration integer
    def parse(self, parser: Parser):
        parser.match(Core.INTEGER, "<decl-integer>")

        # Check if the token is id, obtain the id name explicitly, and advance the scanner
        if parser.scanner.currentToken() != Core.ID:
            parser.error("Invalid derivation for <decl-integer>: expected " + 
                         Core.ID.name + 
                         " but found " + 
                         parser.scanner.currentToken().name)
        self.integerID = parser.scanner.getID()
        parser.scanner.nextToken()

        parser.match(Core.SEMICOLON, "<decl-integer>")

    # Print the declaration integer
    def print(self, indent=1):
        pre = "  " * indent
        print(pre + "integer " + self.integerID + ";")

    # declare id as integer if it is not already declared, else report an error
    def semanticCheck(self, semantic_Checker):
        semantic_Checker.declare(self.integerID, "integer")

    def execute(self, memory):
        memory.declare_integer(self.integerID)

# <decl-obj> ::= object id ;
class Decl_Obj:
    def __init__(self):
        self.objectID = None

    # Parse the declaration object
    def parse(self, parser: Parser):
        parser.match(Core.OBJECT, "<decl-obj>")

        # Check if the token is id, obtain the id name explicitly, and advance the scanner
        if parser.scanner.currentToken() != Core.ID:
            parser.error("Invalid derivation for <decl-obj>: expected " + 
                         Core.ID.name + 
                         " but found " + 
                         parser.scanner.currentToken().name)
        self.objectID = parser.scanner.getID()
        parser.scanner.nextToken()

        parser.match(Core.SEMICOLON, "<decl-obj>")

    # Print the declaration object
    def print(self, indent=1):
        prefix = "  " * indent
        print(prefix + "object " + self.objectID + ";")

    # declare id as object if it is not already declared, else report an error
    def semanticCheck(self, semantic_Checker):
        semantic_Checker.declare(self.objectID, "object")

    def execute(self, memory):
        memory.declare_object(self.objectID)

# <stmt-seq> ::= <stmt> | <stmt><stmt-seq>
class StmtSeq:
    def __init__(self):
        self.stmt = None
        self.stmtSeq = None

    # Parse the statement sequence
    def parse(self, parser: Parser):
        # Parse the shared statement of two derivation alternatives
        self.stmt = Stmt()
        self.stmt.parse(parser)

        # Parse the optional statement sequence
        # The first set for statement sequence is {id, if, for, print, read, object, integer}
        current_Token = parser.scanner.currentToken()
        if current_Token in (Core.ID, Core.IF, Core.FOR, Core.PRINT, Core.READ, Core.OBJECT, Core.INTEGER):
            self.stmtSeq = StmtSeq()
            self.stmtSeq.parse(parser)

    # Print the statement sequence
    def print(self, indent=1):
        self.stmt.print(indent)
        if self.stmtSeq is not None:
            self.stmtSeq.print(indent)

    # Perform semantic analysis on the statement, and statement sequence when applicable
    def semanticCheck(self, semantic_Checker):
        self.stmt.semanticCheck(semantic_Checker)
        if self.stmtSeq is not None:
            self.stmtSeq.semanticCheck(semantic_Checker)

    def execute(self, memory):
        self.stmt.execute(memory)
        if self.stmtSeq is not None:
            self.stmtSeq.execute(memory)

# <stmt> ::= <assign> | <if> | <loop> | <print> | <read> | <decl>
class Stmt:
    def __init__(self):
        self.statement = None

    # Parse the statement
    def parse(self, parser: Parser):
        # Derive and parse the statement based on the current token
        current_Token = parser.scanner.currentToken()
        # The first set for assign statement is {id}
        if current_Token == Core.ID:
            self.statement = Assign()
        # The first set for if statement is {if}
        elif current_Token == Core.IF:
            self.statement = If()
        # The first set for loop statement is {for}
        elif current_Token == Core.FOR:
            self.statement = Loop()
        # The first set for print statement is {print}
        elif current_Token == Core.PRINT:
            self.statement = Print()
        # The first set for read statement is {read}
        elif current_Token == Core.READ:
            self.statement = Read()
        # The first set for declaration statement is {object, integer}
        elif current_Token in (Core.OBJECT, Core.INTEGER):
            self.statement = Decl()
        # Report an error if the token is not in any of the first sets
        else:
            parser.error("Invalid derivation for <stmt>: expected " + 
                Core.ID.name + ", " + 
                Core.IF.name + ", " + 
                Core.FOR.name + ", " + 
                Core.PRINT.name + ", " + 
                Core.READ.name + ", " + 
                Core.OBJECT.name + ", or " + 
                Core.INTEGER.name + " but found " + 
                current_Token.name)
        self.statement.parse(parser)

    # Print the statement
    def print(self, indent=1):
        self.statement.print(indent)

    # Perform semantic analysis on the statement derivation
    def semanticCheck(self, semantic_Checker):
        self.statement.semanticCheck(semantic_Checker)

    def execute(self, memory):
        self.statement.execute(memory)

# <assign> ::= id = <expr> ; | id [ string ] = <expr> ; | id = new object( string, <expr> ); | id : id ;
class Assign:
    def __init__(self):
        self.expr = None
        self.print_Option = None
        self.id1 = None
        self.id2 = None
        self.string = None

    # Parse the assignment statement
    def parse(self, parser: Parser):
        # Shared token: id by all derivations
        # Obtain the first id, check if the token is id, and advance the scanner
        self.id1 = parser.scanner.getID()
        parser.match(Core.ID, "<assign>")

        current_Token = parser.scanner.currentToken()

        # default derivation: id = <expr> ;
        self.print_Option = 1

        # Case1: the second token is ASSIGN
        if current_Token == Core.ASSIGN:
            parser.scanner.nextToken()
            # In Case1: if the current token is not in the first set of <expr>, 
            # derivation: id = new object( string, <expr> ); 
            if parser.scanner.currentToken() not in (Core.ID, Core.CONST, Core.LPAREN):
                parser.match(Core.NEW, "<assign>")
                parser.match(Core.OBJECT, "<assign>")
                parser.match(Core.LPAREN, "<assign>")

                # Check if the token is string, obtain the string explicitly, and advance the scanner
                if parser.scanner.currentToken() != Core.STRING:
                    parser.error("Invalid derivation for <assign>: expected " + 
                        Core.STRING.name + 
                        " but found " + 
                        parser.scanner.currentToken().name)
                self.string = parser.scanner.getString()
                parser.scanner.nextToken()

                parser.match(Core.COMMA, "<assign>")

                self.print_Option = 0

            # Shared token: expr by Case1
            self.expr = Expr()
            self.expr.parse(parser)

            # Handle the additional RPAREN in id = new object( string, <expr> );
            if self.print_Option == 0:
                parser.match(Core.RPAREN, "<assign>")
        
        # Case2: the second token is LSQUARE
        # Derivation: id [ string ] = <expr> ;
        elif current_Token == Core.LSQUARE:
            parser.scanner.nextToken()

            # Check if the token is string, obtain the string explicitly, and advance the scanner
            if parser.scanner.currentToken() != Core.STRING:
                parser.error("Invalid derivation for <assign>: expected " + 
                    Core.STRING.name + 
                    " but found " + 
                    parser.scanner.currentToken().name)
            self.string = parser.scanner.getString()
            parser.scanner.nextToken()

            parser.match(Core.RSQUARE, "<assign>")
            parser.match(Core.ASSIGN, "<assign>")

            self.expr = Expr()
            self.expr.parse(parser)

            self.print_Option = 2
        
        # Case3: the second token is COLON
        # Derivation: id : id ;
        elif current_Token == Core.COLON:
            parser.scanner.nextToken()
            # Check if the token is id, obtain the id name explicitly, and advance the scanner
            if parser.scanner.currentToken() != Core.ID:
                parser.error("Invalid derivation for <assign>: expected " + 
                             Core.ID.name + 
                             " but found " + 
                             parser.scanner.currentToken().name)
            self.id2 = parser.scanner.getID()
            parser.scanner.nextToken()

            self.print_Option = 3
        
        # Case4: the second token is not in any of the first sets, report an error
        else:
            parser.error("Invalid derivation for <assign>: expected " + 
                Core.ASSIGN.name + ", " + 
                Core.COLON.name +  ", or " + 
                Core.LSQUARE.name + " but found " + 
                current_Token.name)
        parser.match(Core.SEMICOLON, "<assign>")

    # print the assignment statement
    def print(self, indent=1):
        pre = "  " * indent
        if self.print_Option == 0:
            print(pre + self.id1 + " = new object( '" + self.string + "', ", end='')
            self.expr.print()
            print(" );")
        elif self.print_Option == 1:
            print(pre + self.id1 + " = ", end='')
            self.expr.print()
            print(" ;")
        elif self.print_Option == 2:
            print(pre + self.id1 + " [ '" + self.string + "' ] = ", end='')
            self.expr.print()
            print(" ;")
        elif self.print_Option == 3:
            print(pre + self.id1 + " : " + self.id2 + " ;")

    # perform semantic checks on the derivation of the assignment statement
    def semanticCheck(self, semantic_Checker):
        if self.print_Option == 0:
            # Verify that the id is declared as an object, instead of an integer
            # for alternative: id = new object( string, <expr> );
            semantic_Checker.objCheck(self.id1)
            self.expr.semanticCheck(semantic_Checker)
        elif self.print_Option == 1:
            # Verify that the id is declared
            semantic_Checker.verify(self.id1)
            self.expr.semanticCheck(semantic_Checker)
        elif self.print_Option == 2:
            # Verify that the id is declared as an object, instead of an integer
            # for alternative: id [ string ] = <expr> ;
            semantic_Checker.objCheck(self.id1)
            self.expr.semanticCheck(semantic_Checker)
        elif self.print_Option == 3:
             # Verify that the ids are declared as objects, instead of integers
            # for alternative: id : id ;
            semantic_Checker.objCheck(self.id1)
            semantic_Checker.objCheck(self.id2)

# <assign> ::= id = <expr> ; | id [ string ] = <expr> ; | id = new object( string, <expr> ); | id : id ;
    def execute(self, memory):
        if self.print_Option == 0:
            # Create a new object with a default key-value pair
            memory.create_object(self.id1, self.string, self.expr.execute(memory))
        elif self.print_Option == 1:
            # Set the value of an integer variable or the default key of an object variable
            memory.set_value(self.id1, self.expr.execute(memory))
        elif self.print_Option == 2:
            # Set the value of a specific key in an object variable
            memory.set_object_key_value(self.id1, self.string, self.expr.execute(memory))
        elif self.print_Option == 3:
            # Reference one object variable to another object variable
            memory.reference(self.id1, self.id2)

# <if> ::= if <cond> then <stmt-seq> end | if <cond> then <stmt-seq> else <stmt-seq> end
class If:
    def __init__(self):
        self.cond = None
        self.stmtSeq1 = None
        self.stmtSeq2 = None

    # Parse the if statement
    def parse(self, parser: Parser):
        # Handle the shared leading tokens by two derivations
        parser.match(Core.IF, "<if>")
        self.cond = Cond()
        self.cond.parse(parser)
        parser.match(Core.THEN, "<if>")
        self.stmtSeq1 = StmtSeq()
        self.stmtSeq1.parse(parser)

        # Check if the token is END, if not, it's the ELSE case
        if (parser.scanner.currentToken() != Core.END):
            parser.match(Core.ELSE, "<if>")
            self.stmtSeq2 = StmtSeq()
            self.stmtSeq2.parse(parser)

        # Check for the shared END token by two derivations
        parser.match(Core.END, "<if>")

    # Print the if statement
    def print(self, indent=1):
        pre = "  " * indent
        print(pre + "if ", end='')
        self.cond.print()
        print(" then ")

        # Pretty print the statement sequence
        # Additional indentation is applied for statement sequences
        self.stmtSeq1.print(indent + 1)
        if self.stmtSeq2 is not None:
            print(pre + "else ")
            self.stmtSeq2.print(indent + 1)
        
        print(pre + "end")

    # Perform semantic checks on the if statement
    def semanticCheck(self, semantic_Checker):
        self.cond.semanticCheck(semantic_Checker)
        # Create a local scope for the then branch
        semantic_Checker.scopes.append({})

        # Perform semantic checks in the local scope
        self.stmtSeq1.semanticCheck(semantic_Checker)

        # Delete the new scope after performing semantic checks
        semantic_Checker.scopes.pop()

        # Create a separate local scope for the else branch
        # Perform semantic checks in the separate local scope if applicable
        if self.stmtSeq2 is not None:
            semantic_Checker.scopes.append({})
            self.stmtSeq2.semanticCheck(semantic_Checker)
            semantic_Checker.scopes.pop()

    def execute(self, memory):
        if self.cond.execute(memory):
            memory.enter_scope()
            self.stmtSeq1.execute(memory)
            memory.exit_scope()
        elif self.stmtSeq2 is not None:
            memory.enter_scope()
            self.stmtSeq2.execute(memory)
            memory.exit_scope()

# <loop> ::= for ( id = <expr> ; <cond> ; <expr> ) do <stmt-seq> end
class Loop:
    def __init__(self):
        self.expr1 = None
        self.id = None
        self.cond = None
        self.expr2 = None
        self.stmtSeq = None

    # Parse the loop statement
    def parse(self, parser: Parser):
        parser.match(Core.FOR, "<loop>")
        parser.match(Core.LPAREN, "<loop>")

        # Check if the token is id, obtain the id name explicitly, and advance the scanner
        if parser.scanner.currentToken() != Core.ID:
            parser.error("Invalid derivation for <loop>: expected " + 
                Core.ID.name + 
                " but found " + 
                parser.scanner.currentToken().name)
        self.id = parser.scanner.getID()
        parser.scanner.nextToken()

        # Check the remaining tokens
        # Parse the expressions, the condition, as well as the statement sequence
        parser.match(Core.ASSIGN, "<loop>")
        self.expr1 = Expr()
        self.expr1.parse(parser)
        parser.match(Core.SEMICOLON, "<loop>")
        self.cond = Cond()
        self.cond.parse(parser)
        parser.match(Core.SEMICOLON, "<loop>")
        self.expr2 = Expr()
        self.expr2.parse(parser)
        parser.match(Core.RPAREN, "<loop>")
        parser.match(Core.DO, "<loop>")
        self.stmtSeq = StmtSeq()
        self.stmtSeq.parse(parser)
        parser.match(Core.END, "<loop>")

    def print(self, indent=1):
        prefix = "  " * indent
        print(prefix + "for ( " + self.id + " = ", end='')
        self.expr1.print()
        print(" ; ", end='')
        self.cond.print()
        print(" ; ", end='')
        self.expr2.print()
        print(" ) do")

        # Pretty print the statement sequence
        # Additional indentation is applied for statement sequences
        self.stmtSeq.print(indent + 1)

        print(prefix + "end")

    def semanticCheck(self, semantic_Checker):
        semantic_Checker.verify(self.id)
        self.expr1.semanticCheck(semantic_Checker)
        self.cond.semanticCheck(semantic_Checker)
        self.expr2.semanticCheck(semantic_Checker)

        # Perform semantic checks in the loop scope
        semantic_Checker.scopes.append({})
        self.stmtSeq.semanticCheck(semantic_Checker)
        semantic_Checker.scopes.pop()

    # <loop> ::= for ( id = <expr> ; <cond> ; <expr> ) do <stmt-seq> end
    def execute(self, memory):
        # Initialize the loop variable with the first expression
        memory.set_value(self.id, self.expr1.execute(memory))

        # Execute the loop while the condition is true
        while self.cond.execute(memory):
            memory.enter_scope()
            self.stmtSeq.execute(memory)
            memory.exit_scope()

            # Update the loop variable with the second expression
            memory.set_value(self.id, self.expr2.execute(memory))

# <print> ::= print ( <expr> ) ;
class Print:
    def __init__(self):
        self.expr = None

    # Parse the print statement
    def parse(self, parser: Parser):
        parser.match(Core.PRINT, "<print>")
        parser.match(Core.LPAREN, "<print>")
        self.expr = Expr()
        self.expr.parse(parser)
        parser.match(Core.RPAREN, "<print>")
        parser.match(Core.SEMICOLON, "<print>")

    # Pretty print the print statement
    def print(self, indent=1):
        prefix = "  " * indent
        print(prefix + "print ( ", end='')
        self.expr.print()
        print(" ) ;")

    # Perform semantic checks on the printed expression
    def semanticCheck(self, semantic_Checker):
        self.expr.semanticCheck(semantic_Checker)

    def execute(self, memory):
        value = self.expr.execute(memory)
        print(value)

# <read> ::= read ( id ) ;
class Read:
    def __init__(self):
        self.id = None

    # Parse the read statement
    def parse(self, parser: Parser):
        parser.match(Core.READ, "<read>")
        parser.match(Core.LPAREN, "<read>")

        # Check if the token is id, obtain the id name explicitly, and advance the scanner
        if parser.scanner.currentToken() != Core.ID:
            parser.error("Invalid derivation for <read>: expected " + 
                Core.ID.name + 
                " but found " + 
                parser.scanner.currentToken().name)
        self.id = parser.scanner.getID()
        parser.scanner.nextToken()

        parser.match(Core.RPAREN, "<read>")
        parser.match(Core.SEMICOLON, "<read>")

    # Pretty print the read statement
    def print(self, indent=1):
        prefix = "  " * indent
        print(prefix + "read ( " + self.id + " ) ;")

    # Verify that the id is declared
    def semanticCheck(self, semantic_Checker):
        semantic_Checker.verify(self.id)

    def execute(self, memory):
        memory.set_value(self.id, memory.read())

# <cond> ::= <cmpr> | not <cond> | [ <cond> ] | <cmpr> or <cond> | <cmpr> and <cond>
class Cond:
    def __init__(self):
        self.cmpr = None
        self.cond = None
        self.print_option = None

    # Parse the condition
    def parse(self, parser: Parser):
        # Case1: the leading token is a compr
        # Derivations: <cmpr> | <cmpr> or <cond> | <cmpr> and <cond>
        if parser.scanner.currentToken() in (Core.ID, Core.CONST, Core.LPAREN):
            # Default option for Case1, where the token is shared by all alternatives in Case1
            # Derivation: <cmpr>
            self.print_option = 0
            self.cmpr = Cmpr()
            self.cmpr.parse(parser)

            # Remaining alternatives of Case1
            # Derivation: (<cmpr> or <cond>, <cmpr> and <cond>)
            current_Token = parser.scanner.currentToken()
            if current_Token in (Core.OR, Core.AND) :
                self.print_option = 1 if current_Token == Core.OR else 2
                parser.scanner.nextToken()
                self.cond = Cond()
                self.cond.parse(parser)

        # Case2: the leading token is in (not, [), not in the first set of <cmpr>
        # Derivations: not <cond> | [ <cond> ]
        elif parser.scanner.currentToken() in (Core.NOT, Core.LSQUARE):
            self.print_option = 3 if parser.scanner.currentToken() == Core.NOT else 4
            parser.scanner.nextToken()
            self.cond = Cond()
            self.cond.parse(parser)
            # Handle the remaining token in [ <cond> ]
            if self.print_option == 4:
                parser.match(Core.RSQUARE, "<cond>")
        else:
        # Case3: the leading token is not in the first sets of all derivation alternatives
            parser.error("Invalid derivation for <cond>: expected " + 
                Core.ID.name + ", " + 
                Core.CONST.name + ", " + 
                Core.LPAREN.name + ", " + 
                Core.NOT.name + ", or " + 
                Core.LSQUARE.name + 
                " but found " + 
                parser.scanner.currentToken().name)

    # Print the parsed condition
    def print(self):
        if self.print_option == 0:
            self.cmpr.print()
        elif self.print_option == 1:
            self.cmpr.print()
            print(" or ", end='')
            self.cond.print()
        elif self.print_option == 2:
            self.cmpr.print()
            print(" and ", end='')
            self.cond.print()
        elif self.print_option == 3:
            print("not ", end='')
            self.cond.print()
        elif self.print_option == 4:
            print("[ ", end='')
            self.cond.print()
            print(" ]", end='')

    # Perform semantic checking on the parsed condition
    def semanticCheck(self, semantic_Checker):
        if self.print_option == 0:
            self.cmpr.semanticCheck(semantic_Checker)
        elif self.print_option == 1:
            self.cmpr.semanticCheck(semantic_Checker)
            self.cond.semanticCheck(semantic_Checker)
        elif self.print_option == 2:
            self.cmpr.semanticCheck(semantic_Checker)
            self.cond.semanticCheck(semantic_Checker)
        elif self.print_option == 3:
            self.cond.semanticCheck(semantic_Checker)
        elif self.print_option == 4:
            self.cond.semanticCheck(semantic_Checker)

    def execute(self, memory):
        if self.print_option == 0:
            return self.cmpr.execute(memory)
        elif self.print_option == 1:
            return self.cmpr.execute(memory) or self.cond.execute(memory)
        elif self.print_option == 2:
            return self.cmpr.execute(memory) and self.cond.execute(memory)
        elif self.print_option == 3:
            return not self.cond.execute(memory)
        elif self.print_option == 4:
            return self.cond.execute(memory)

# <cmpr> ::= <expr> == <expr> | <expr> < <expr>
class Cmpr:
    def __init__(self):
        self.expr1 = None
        self.expr2 = None
        self.print_Option = None
    
    # parse the comparison
    def parse(self, parser: Parser):
        # Parse the shared expression1 by all alternatives
        self.expr1 = Expr()
        self.expr1.parse(parser)

        # Check if the operator token is valid for all alternatives
        if parser.scanner.currentToken() not in (Core.EQUAL, Core.LESS):
            parser.error("Invalid derivation for <cmpr>: expected " + 
                Core.EQUAL.name + " or " + 
                Core.LESS.name + 
                " but found " + 
                parser.scanner.currentToken().name)
        
        # Determine the print option based on the current token
        self.print_Option = 0 if parser.scanner.currentToken() == Core.EQUAL else 1

        # Parse the shared expression2 by all alternatives
        parser.scanner.nextToken()
        self.expr2 = Expr()
        self.expr2.parse(parser)

    # Print the parsed comparison
    def print(self):
        self.expr1.print()
        print(" == ", end='') if self.print_Option == 0 else print(" < ", end='')
        self.expr2.print()

    # Perform semantic checking on the parsed expressions
    def semanticCheck(self, semantic_Checker):
        self.expr1.semanticCheck(semantic_Checker)
        self.expr2.semanticCheck(semantic_Checker)

    def execute(self, memory):
        value1 = self.expr1.execute(memory)
        value2 = self.expr2.execute(memory)
        if self.print_Option == 0:
            return value1 == value2
        else:
            return value1 < value2

# <expr> ::= <term> | <term> + <expr> | <term> – <expr>
class Expr:
    def __init__(self):
        self.term = None
        self.print_Option = None
        self.expr = None

    # parse the term, and expression when applicable
    def parse(self, parser: Parser):
        # parse the shared term by all alternatives
        self.term = Term()
        self.term.parse(parser)
        # default option: <term>
        self.print_Option = 0

        # Check if the operator token is valid for all alternatives other than the default
        current_Token = parser.scanner.currentToken()
        if current_Token in (Core.ADD, Core.SUBTRACT):
            self.print_Option = 1 if current_Token == Core.ADD else 2
            parser.scanner.nextToken()
            self.expr = Expr()
            self.expr.parse(parser)

    # Print the parsed term, and expression when applicable
    def print(self):
        self.term.print()
        if self.print_Option in (1, 2):
            print(" + ", end='') if self.print_Option == 1 else print(" - ", end='')
            self.expr.print()

    # Perform semantic checking on the parsed term, and expression when applicable
    def semanticCheck(self, semantic_Checker):
        self.term.semanticCheck(semantic_Checker)
        if self.print_Option in (1, 2):
            self.expr.semanticCheck(semantic_Checker)

    # Execute the parsed term, and expression when applicable
    def execute(self, memory):
        value1 = self.term.execute(memory)
        if self.print_Option in (1, 2):
            value2 = self.expr.execute(memory)
            if self.print_Option == 1:
                return value1 + value2
            else:
                return value1 - value2
        return value1

# <term> ::= <factor> | <factor> * <term> | <factor> / <term>
class Term:
    def __init__(self):
        self.factor = None
        self.print_Option = None
        self.term = None

    # parse the factor, and term when applicable
    def parse(self, parser: Parser):
        # Parse the shared factor by all alternatives
        self.factor = Factor()
        self.factor.parse(parser)
        # default option: <factor>
        self.print_Option = 0

        # Check if the operator token is valid for all alternatives other than the default
        current_Token = parser.scanner.currentToken()
        if current_Token in (Core.MULTIPLY, Core.DIVIDE):
            self.print_Option = 1 if current_Token == Core.MULTIPLY else 2
            parser.scanner.nextToken()
            self.term = Term()
            self.term.parse(parser)

    # Print the parsed factor, and term when applicable
    def print(self):
        self.factor.print()
        if self.print_Option in (1, 2):
            print(" * ", end='') if self.print_Option == 1 else print(" / ", end='')
            self.term.print()
    
    # Perform semantic checking on the parsed factor, and term when applicable
    def semanticCheck(self, semantic_Checker):
        self.factor.semanticCheck(semantic_Checker)
        if self.print_Option in (1, 2):
            self.term.semanticCheck(semantic_Checker)

    # Execute the parsed factor, and term when applicable
    def execute(self, memory):
        value1 = self.factor.execute(memory)
        if self.print_Option in (1, 2):
            value2 = self.term.execute(memory)
            if self.print_Option == 1:
                return value1 * value2
            else:
                if value2 == 0:
                    memory.error("Division by zero error")
                return int(value1 / value2)
        return value1

# <factor> ::= id | id [ string ] | const | ( <expr> )
class Factor:
    def __init__(self):
        self.id = None
        self.string = None
        self.print_Option = None
        self.const = None
        self.expr = None

    # parse the factor based on its type
    def parse(self, parser: Parser):
        current_Token = parser.scanner.currentToken()

        # Case1: the first token is an identifier
        if current_Token == Core.ID:
            # Default option: id
            self.print_Option = 0

            # Obtain the id name explicitly, and advance the scanner
            self.id = parser.scanner.getID()
            parser.scanner.nextToken()

            # Derivation: id [ string ]
            if parser.scanner.currentToken() == Core.LSQUARE:
                parser.scanner.nextToken()

                # Check if the next token is a string, obtain it, and advance the scanner
                if parser.scanner.currentToken() != Core.STRING:
                    parser.error("Invalid derivation for <factor>: expected " + 
                        Core.STRING.name + 
                        " but found " + 
                        parser.scanner.currentToken().name)
                self.print_Option = 1
                self.string = parser.scanner.getString()
                parser.scanner.nextToken()

                parser.match(Core.RSQUARE, "<factor>")

        # Case2: the first token is a constant or left parenthesis
        elif current_Token in (Core.CONST, Core.LPAREN):
            self.print_Option = 2 if current_Token == Core.CONST else 3

            # Obtain the constant if the token is a constant
            if self.print_Option == 2:
                self.const = parser.scanner.getCONST()
                parser.scanner.nextToken()
            
            # If the token is a left parenthesis, parse the expression after it
            else:
                parser.scanner.nextToken()
                self.expr = Expr()
                self.expr.parse(parser)
                parser.match(Core.RPAREN, "<factor>")
        
        # Case3: the first token is invalid
        else:
            parser.error("Invalid derivation for <factor>: expected " + 
                Core.ID.name + ", " +
                Core.CONST.name + ", or " +
                Core.LPAREN.name + 
                " but found " + 
                parser.scanner.currentToken().name)

    # print the factor based on its type
    def print(self):
        if self.print_Option == 0:
            print(self.id, end='')
        elif self.print_Option == 1:
            print(self.id + " [ '" + self.string + "' ]", end='')
        elif self.print_Option == 2:
            print(self.const, end='')
        elif self.print_Option == 3:
            print("( ", end='')
            self.expr.print()
            print(" )", end='')

    # perform semantic check on the factor
    def semanticCheck(self, semantic_Checker):
        # verify that the variable is declared for alternative: id
        if self.print_Option == 0:
            semantic_Checker.verify(self.id)
        # verify that the variable is declared as an object for alternative: id [ string ], instead of an integer
        elif self.print_Option == 1:
            semantic_Checker.objCheck(self.id)
        elif self.print_Option == 2:
            pass
        # Perform semantic check on the expression for alternative: ( expr )
        elif self.print_Option == 3:
            self.expr.semanticCheck(semantic_Checker)

    def execute(self, memory):
        if self.print_Option == 0:
            return memory.get_value(self.id)
        elif self.print_Option == 1:
            return memory.get_object_key_value(self.id, self.string)
        elif self.print_Option == 2:
            return self.const
        elif self.print_Option == 3:
            return self.expr.execute(memory)

class SemanticChecker:
    def __init__(self):
        # Maintain a stack of scopes that stores all active scopes.
        # self.scopes[0] is the global scope; self.scopes[1] is the first nested scope, etc.
        # Use append to enter the new scope, and pop to exit the current scope
        self.scopes = [{}]
    # verify that a variable is declared
    def verify(self, variable):
        for scope in reversed(self.scopes):
            if variable in scope:
                return scope[variable]
        self.error("variable " + variable + " not declared")
    # Report an error, and exit
    def error(self, message):
        print("ERROR: " + message)
        raise SystemExit
    # Declare a variable
    def declare(self, variable, variableType):
        # Check if the variable is already declared in the current scope (doubly declared)
        if variable in self.scopes[-1]:
            self.error("variable " + variable + " already declared")
        self.scopes[-1][variable] = variableType
    # Check if a variable is not declared appropriately as an object
    def objCheck(self, variable):
        variableType = self.verify(variable)
        if variableType != "object":
            self.error("variable " + variable + " is not an object")