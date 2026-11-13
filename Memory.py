from Core import Core
class Memory:
    def __init__(self, dataScanner):
       # Initialize the Memory class with a global scope and a list of local scopes
       self.globalScope = {}
       self.callstack = [[]]
       self.functions = {}
       self.dataScanner = dataScanner

       self.reachableObjects = 0

    def error(self, message):
        # Handle errors by printing the error message
        print("ERROR: " + message)
        raise SystemExit

    def enter_frame(self):
        # Enter a new call frame by appending an empty list to the call stack
        self.callstack.append([{}])

    # Exit the current call frame and release any object references it holds
    def exit_frame(self):
        if len(self.callstack) > 1:
            for scope in self.callstack[-1]:
                for entry in scope.values():
                    if entry["type"] == "object" and entry["value"] is not None:
                        entry["value"]["refCount"] -= 1
                        if entry["value"]["refCount"] == 0:
                            entry["value"] = None
                            self.reachableObjects -= 1
                            print("gc:" + str(self.reachableObjects))
            self.callstack.pop()
        else:
            self.error("No frame to exit.")

    def enter_scope(self):
        # Enter a new local scope by appending an empty dictionary to the list of local scopes
        self.callstack[-1].append({})

    # Exit the current local scope and release any object references it holds
    def exit_scope(self):
        # Exit the current local scope by popping the last dictionary from the list of local scopes
        if self.callstack[-1]:
            for entry in self.callstack[-1][-1].values():
                if entry["type"] == "object" and entry["value"] is not None:
                    entry["value"]["refCount"] -= 1
                    if entry["value"]["refCount"] == 0:
                        entry["value"] = None
                        self.reachableObjects -= 1
                        print("gc:" + str(self.reachableObjects))
            self.callstack[-1].pop()
        else:
            self.error("No local scope to exit.")

    # Exit the global scope and release any object references it holds
    def exit_global_scope(self):
        # Exit the global scope by clearing the global scope dictionary
        for entry in self.globalScope.values():
            if entry["type"] == "object" and entry["value"] is not None:
                entry["value"]["refCount"] -= 1
                if entry["value"]["refCount"] == 0:
                    entry["value"] = None
                    self.reachableObjects -= 1
                    print("gc:" + str(self.reachableObjects))
        self.globalScope.clear()

    def current_scope(self):
        # Return the current local scope, or the global scope if no local scopes exist
        if self.callstack[-1]:
            return self.callstack[-1][-1]
        else:
            return self.globalScope

    def find_variable(self, name):
        # Find a variable by name in the current local scope or global scope
        for scope in reversed(self.callstack[-1]):
            if name in scope:
                return scope[name]
        if name in self.globalScope:
            return self.globalScope[name]
        self.error("Variable " + name + " not found.")

    def get_type(self, name):
        # Get the type of a variable by name in the current local scope or global scope
        return self.find_variable(name)["type"]

    def get_value(self, name):
        # Get the value of a variable by name in the current local scope or global scope
        entry = self.find_variable(name)
        if entry["type"] == "integer":
            return entry["value"]
        elif entry["type"] == "object":
            obj = self.get_object(name)
            return obj["values"][obj["defaultKey"]]
        self.error("Variable " + name + " not found.")

    def declare_integer(self, name):
        # Declare an integer variable in the current scope
        scope = self.current_scope()
        if name in scope:
            self.error("Variable " + name + " already declared.")
        scope[name] = {"type": "integer", "value": 0}  # Initialize with type integer and default value 0

    def declare_object(self, name):
        # Declare an object variable in the current scope
        scope = self.current_scope()
        if name in scope:
            self.error("Variable " + name + " already declared.")
        scope[name] = {"type": "object", "value": None}  # Initialize with type object and default value None

    def create_object(self, name, key, value):
        # Create a new object with a default key-value pair
        entry = self.find_variable(name)
        if entry["type"] != "object":
            self.error("Variable " + name + " is not an object.")
        if entry["value"] is not None:
            entry["value"]["refCount"] -= 1
            if entry["value"]["refCount"] == 0:
                entry["value"] = None
                self.reachableObjects -= 1
                print("gc:" + str(self.reachableObjects))
        entry["value"] = {"values" : {key: value}, "defaultKey": key, "refCount": 1}  # Initialize the reference count
        self.reachableObjects += 1
        print("gc:" + str(self.reachableObjects))

    def get_object(self, name):
        # Get the object variable by name
        entry = self.find_variable(name)
        if entry["type"] != "object":
            self.error("Variable " + name + " is not an object.")
        if entry["value"] is None:
            self.error("Object " + name + " has not been created yet.")
        return entry["value"]

    def set_object_key_value(self, name, key, value):
        # Set the value of a specific (can be new/existed) key in an object variable
        obj = self.get_object(name)
        obj["values"][key] = value

    def get_object_key_value(self, name, key):
        # Get the value of a specific key in an object variable
        obj = self.get_object(name)
        if key in obj["values"]:
            return obj["values"][key]
        else:
            self.error("Key " + key + " not found in object " + name + ".")

    def set_value(self, name, value):
        # Set the value of a variable by name in the current local scope or global scope
        entry = self.find_variable(name)
        if entry["type"] == "integer":
            entry["value"] = value
        elif entry["type"] == "object":
            obj = self.get_object(name)
            obj["values"][obj["defaultKey"]] = value

    # Bind an object argument to a parameter in the current scope (function call)
    def bind_object(self, name, argument):
        self.current_scope()[name] = {"type": "object", "value": argument["value"]}
        if argument["value"] is not None:
            argument["value"]["refCount"] += 1

    def reference(self, id1, id2):
        # Return a reference to a variable by name in the current local scope or global scope
        entry1 = self.find_variable(id1)
        entry2 = self.find_variable(id2)
        if entry1["type"] != "object" or entry2["type"] != "object":
            self.error("Both variables must be objects to reference the same object.")
        if entry1["value"] is not entry2["value"]:
            if entry1["value"] is not None:
                entry1["value"]["refCount"] -= 1
                if entry1["value"]["refCount"] == 0:
                    self.reachableObjects -= 1
                    print("gc:" + str(self.reachableObjects))
            if entry2["value"] is not None:
                entry2["value"]["refCount"] += 1
            entry1["value"] = entry2["value"]

    def read(self):
        # Read an integer value from the data scanner and return it
        if self.dataScanner.currentToken() == Core.EOS:
            self.error("No more data to read.")
        value = self.dataScanner.getCONST()
        self.dataScanner.nextToken()
        return value
