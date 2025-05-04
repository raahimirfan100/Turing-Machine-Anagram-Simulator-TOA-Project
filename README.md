# Turing Machine Anagram Simulator

A visual simulator for a Turing Machine that checks whether two strings are anagrams of each other. This educational tool demonstrates how a Turing Machine can be used to solve the anagram problem.

## Overview

This project implements a Turing Machine that determines if two strings are anagrams - meaning they contain the same characters in a different order. The implementation includes both a graphical simulator for visualizing the execution and a command-line interface for quick checks.

## Features

- **Visual Simulation**: Step-by-step visualization of the Turing Machine's execution
- **Detailed Execution Log**: View each state transition and tape manipulation
- **Dual Interface**: Choose between GUI and command-line usage
- **Case Sensitivity Options**: Enable or disable case-sensitive comparisons

## Requirements

- Python 3.8+
- PyQt5 (for GUI mode)

You can install the requirements using pip:

```bash
pip install PyQt5
```

Or, install all requirements from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode

To run the graphical simulator:

```bash
python main.py [string1] [string2] [-h/--help]
```

The interactive GUI allows you to:

- Visualize the Turing Machine tape
- Step through the execution one transition at a time
- See the current state and position of the head
- Track the algorithm's progress

### Terminal Mode

For command-line usage:

```bash
python terminal.py [string1] [string2] [-c/--case-sensitive] [-h/--help]
```

If no arguments are provided, the terminal interface will prompt you to enter the required information.

## Examples

Check if "state" and "taste" are anagrams:

```bash
# Using GUI
python main.py state taste

# Using terminal
python terminal.py state taste
python terminal.py sTaTe taSTe -c  # case-sensitive testing
```

## How It Works

The Turing Machine algorithm:

1. Takes two strings separated by a '#' character on the tape
2. For each character in the first string:
   - Marks it as processed (replaces with '\*')
   - Searches for a matching character in the second string
   - If found, marks it as matched (replaces with 'X') and continues
   - If not found, rejects the input
3. After processing the first string, checks if any unmarked characters remain in the second string
4. Accepts if all characters are properly matched, rejects otherwise

## Project Structure

- `turing_machine.py` - Core Turing Machine implementation
- `simulator_ui.py` - PyQt5-based GUI components
- `main.py` - Entry point for the GUI application
- `terminal.py` - Command line interface for anagram checking

## Educational Value

This simulator helps students understand:

- Turing Machine concepts
- State transitions and tape operations
- Algorithm design for string processing
- Computational theory basics

## License

MIT License
