from Scanner import Scanner
from Parser import Parser
from Core import Core
from Memory import Memory
import sys

def main():
  # Initialize the scanner with the input file
  scanner = Scanner(sys.argv[1])
  dataScanner = Scanner(sys.argv[2])
  # Initialize the parser with the scanner
  parser = Parser(scanner)

  # Generate the parse tree and perform semantic checks
  parser.parse()
  parser.semanticCheck()

  # Execute the program using the memory initialized with the data scanner
  memory = Memory(dataScanner)
  parser.execute(memory)

if __name__ == "__main__":
  main()