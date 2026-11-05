Name: Yibo Su
CSE 3341 Project3


Files:
-- Core.py
	-- Defines the Core enum containing all token types (keywords, symbols, and specials) used by the scanner and parser.
-- Scanner.py
	-- Implements the scanner for the Core language, which reads the input file, tokenizes, and returns the current token and the values of identifiers, constants, and strings.
-- Parser.py
	-- Implements the recursive descent parser, parse tree, semantic checker, pretty printer, and executor.
-- Main.py
	-- Creates Code and Data Scanner and Parser, parses the input program, performs semantic checking, initializes memory, and then executes the program.
-- Memory.py
	-- Manages global and local scopes, object values, object references, and values read from .data files.

-- README.txt
	-- Demonstrates the project design, files, and testing details.


Design:
The Main.py first calls Scanner.py and Parser.py to construct the parser tree for the Core program. And then, the semantic checker detects declaration errors and typing errors before execution. After parsing and semantic checking, the Main.py creates a Memory object and starts execution from the root of the parse tree. The execution procedure maintains the same recursive descent structure as parsing. Each grammar class has an execution function. For nodes like expression, term, factor, comparison, and condition, they return values (either True/False or numerical values), while the others mainly executes their child non-terminals. The global scope is represented by a dictionary, while the local scopes are represented by a list of dictionaries. The global scope stores the variables declared before the procedure body. In local scopes, entering and leaving a scope are enabled by appending a new dictionary and popping the most recent dictionary. Since the local scopes are represented by a list of dictionaries, nested scopes are enabled. And, the variable lookup check starts from the innermost scope to outer scopes, which allows hiding a variable with the same name in the outer scope. There are two kinds of variables defined in the Core program, integer and object. By declaring an integer, the variable's type will be set to "integer", and its value will be initialized to 0. Declaring an object variable is more complex since it adopts reference semantics, instead of value semantics as integers do. When declared, the value of an object variable is initialized to null, and its type is set to "object". And, when an object is created, the "value" field of an object variable stores a reference to a dictionary that contains two fields, "values" (the key-value map) and "defaultKey" (the default key records the key used when the object is created, and is used to access or assign the object without specifying a string key).


Special features:
-- Two (or more) object variables can reference the same dictionary, so changes made through one reference variable can be applied across all reference variables.
-- By using a list of dictionaries, the interpreter supports nested local scopes. And, variable lookup procedure starts from the innermost scope and proceeds outward, which allows the existence of a local variable with the same name as the one declared in outer scopes. However, the interpreter still prohibits doubly declared variables in the same scope.
-- To read values from .data file, the interpreter uses a second Scanner instance. Each execution of a read statement consumes one integer from the data input. And when the scanner reaches the end of stream (the current token is Core.EOS), it will report an error if another read statement is executed.
-- Expression and term execution preserve the right-associative structure defined in the Core grammar. For example, 1 - 2 - 3 is evaluated as 1 - (2 - 3).


Testing:
-- tester.sh: The program was tested on the provided tester on coelinux env, the result is as follows:
	-- Correct cases: 30/30
	-- Error cases: 4/4
-- additional tests: I also tested right-associative arithmetic, nested scopes and variable hiding, object key updates,
	and shared object references.

Known bugs:
None
