import sys
import argparse
from PyQt5.QtWidgets import QApplication
from simulator_ui import TuringMachineSimulator

def parse_arguments():
    """
    grabs any command line args the user might have entered
    
    returns:
        the parsed arguments for string1 and string2
    """
    parser = argparse.ArgumentParser(description='Turing Machine Anagram Simulator - GUI Mode')
    parser.add_argument('string1', nargs='?', help='First string to check')
    parser.add_argument('string2', nargs='?', help='Second string to check')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    # start up the gui app
    app = QApplication(sys.argv)
    
    # default test case if user doesn't provide input
    tape_input = "abab#baba"
    
    # use command line args if they gave us any
    if args.string1 and args.string2:
        tape_input = f"{args.string1}#{args.string2}"
    
    # initialize & launch the simulator
    sim = TuringMachineSimulator(tape_input)
    sim.show()
    
    # kick off the main event loop
    sys.exit(app.exec_())