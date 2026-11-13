# Core Interpreter

**Author:** Yibo Su

## Files

- **`Core.py`** — Defines the `Core` enum containing all token types (keywords, symbols, and special tokens) used by the scanner and parser.
- **`Scanner.py`** — Implements the scanner for the Core language. It reads the input file, tokenizes it, and returns current tokens and identifier, constant, and string values.
- **`Parser.py`** — Implements the recursive descent parser, parse tree, semantic checker, pretty printer, and executor, including procedure declarations, calls, formal parameters, and related semantic checks.
- **`Main.py`** — Initializes the code and data scanners and parser, parses the program, performs semantic checking, initializes memory, and executes the program.
- **`Memory.py`** — Manages global and local scopes, the call stack, object values and references, reference counts, reachable objects, and data read from `.data` files.
- **`README.md`** — Describes the project design, components, features, and tests.

## Design

### Parsing, semantic checking, and execution

`Main.py` uses `Scanner.py` and `Parser.py` to construct a parse tree for the Core program. The parser also collects procedure names for procedure calls. Before execution, the semantic checker detects declaration and type errors, duplicate procedure names, invalid procedure calls, and duplicate formal parameters.

After parsing and semantic checking, `Main.py` creates a `Memory` object and starts execution from the root of the parse tree. Execution follows the recursive-descent structure of parsing, with an execution method for each grammar class. Nodes such as expressions, terms, factors, comparisons, and conditions return numerical or Boolean values, while other nodes mainly execute their child nonterminals.

### Scopes and call stack

The global scope is represented by a dictionary. Local scopes are maintained as lists of dictionaries within call-stack frames. Each procedure call pushes a new frame, and that frame is popped after the procedure finishes. Separate frames allow recursive calls.

Entering a local scope appends a dictionary, and leaving it removes the most recent dictionary. Variable lookup proceeds from the innermost scope outward, allowing inner declarations to hide variables with the same name in outer scopes.

### Variables and objects

Core supports two variable types:

- **Integer:** initialized to `0` and stored with value semantics.
- **Object:** initialized to `null` and stored with reference semantics.

An object variable's value can reference a dictionary containing:

- **`values`** — The object's key–value mapping.
- **`defaultKey`** — The key provided when the object was created, used when accessing or assigning the object without an explicit string key.
- **`refCount`** — The number of object variables currently referencing the object.

### Procedure calls and parameter passing

`Memory.py` maintains a `functions` dictionary mapping procedure names to their parse-tree nodes. When a procedure is called, the interpreter finds the corresponding node and executes its body.

Object arguments use **call-by-sharing**. The `bind_object` method creates a formal parameter entry that points to the same object as the argument and increments its `refCount`. As a result, mutations to the shared object are visible to both caller and callee.

### Reference counting and garbage collection

`Memory.py` maintains `reachableObjects`, the number of currently reachable objects. Object reference creation, reassignment, and scope exit update the relevant `refCount`. When an object's `refCount` reaches `0`, `reachableObjects` decreases because the object is no longer reachable.

Whenever the reachable-object count changes, the interpreter reports `gc:n`, where `n` is the current count.

## Special Features

- Supports procedure declarations and calls; procedure declarations are permitted only in the outer declaration sequence, not inside procedure bodies.
- Supports recursion with an independent call-stack frame for each call.
- Implements call-by-sharing for object parameters through `Memory.py`'s `bind_object` method.
- Uses a `functions` dictionary to map procedure names to parse-tree nodes.
- Collects procedure names before checking procedure bodies, allowing calls to procedures declared later and enabling duplicate-name checks.
- Uses a separate semantic scope for formal parameters of each procedure, enabling duplicate-parameter checks.
- Uses object reference counting and reachable-object tracking for garbage collection.
