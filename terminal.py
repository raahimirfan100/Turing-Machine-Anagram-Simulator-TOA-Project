import argparse
import sys
import time
from turing_machine import TuringMachine
from colorama import init, Fore, Back, Style
import os
import platform

# initialize colorama
init(autoreset=True)

# constants for consistent styling
COLORS = {
    "HEADER": Fore.CYAN + Style.BRIGHT,
    "SECTION": Fore.YELLOW,
    "SUCCESS": Fore.GREEN + Style.BRIGHT,
    "ERROR": Fore.RED + Style.BRIGHT,
    "INPUT": Fore.YELLOW,
    "NOTE": Fore.CYAN,
    "BLANK": Fore.LIGHTBLACK_EX,
    "PROCESSED": Fore.YELLOW,
    "MATCHED": Fore.GREEN,
    "SEPARATOR": Fore.RED,
    "TEXT": Fore.WHITE,
    "STATE": Fore.MAGENTA + Style.BRIGHT,
}

SYMBOLS = {
    "SUCCESS": "✓",
    "ERROR": "✗",
    "DIVIDER": "="
}

# animation settings
ANIMATION_SPEED = 0.05  # seconds between animation frames

# terminal size detection
try:
    terminal_width = os.get_terminal_size().columns
except:
    terminal_width = 80

def clear_screen():
    # cross-platform clear screen
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header(text, width=None):
    width = width or terminal_width
    # pretty header
    print(COLORS["HEADER"] + SYMBOLS["DIVIDER"] * width)
    print(COLORS["HEADER"] + text.center(width))
    print(COLORS["HEADER"] + SYMBOLS["DIVIDER"] * width + Style.RESET_ALL)

def print_section(text, width=None):
    width = width or terminal_width
    # section divider
    print(COLORS["SECTION"] + "-" * width)
    print(COLORS["SECTION"] + text.center(width))
    print(COLORS["SECTION"] + "-" * width + Style.RESET_ALL)

def format_tape_display(tape, head_position, width=None):
    width = width or terminal_width
    # display tape with current head position highlighted
    tape_str = ''.join(tape)
    
    # ensure tape is not too wide for display
    if len(tape_str) > width - 10:
        start_pos = max(0, head_position - width//3)
        end_pos = min(len(tape_str), start_pos + width - 10)
        tape_str = "..." + tape_str[start_pos:end_pos] + "..."
        # adjust head position for truncated display
        head_position = head_position - start_pos + 3 if start_pos > 0 else head_position
    
    # create head pointer and highlighted current position
    formatted_tape = ""
    for i, char in enumerate(tape_str):
        if i == head_position:
            formatted_tape += Back.GREEN + Fore.BLACK + char + Style.RESET_ALL
        else:
            # color code different symbols
            if char == '_':
                formatted_tape += COLORS["BLANK"] + char + Style.RESET_ALL
            elif char == '*':
                formatted_tape += COLORS["PROCESSED"] + char + Style.RESET_ALL
            elif char == 'X':
                formatted_tape += COLORS["MATCHED"] + char + Style.RESET_ALL
            elif char == '$':
                formatted_tape += COLORS["SEPARATOR"] + char + Style.RESET_ALL
            else:
                formatted_tape += COLORS["TEXT"] + char + Style.RESET_ALL
    
    # create head indicator for clarity
    head_indicator = ' ' * head_position + COLORS["MATCHED"] + '↑' + Style.RESET_ALL
    
    return [formatted_tape, head_indicator]

def animate_text(text, color=COLORS["HEADER"]):
    # animate text typing
    for char in text:
        print(color + char + Style.RESET_ALL, end='', flush=True)
        time.sleep(ANIMATION_SPEED/2)
    print()

def show_turing_machine_explanation():
    clear_screen()
    print_header("HOW TURING MACHINES WORK", width=70)
    
    explanations = [
        "A Turing Machine is a mathematical model of computation that defines an",
        "abstract machine which manipulates symbols on a strip of tape according",
        "to a table of rules.",
        "",
        "For our anagram checker:",
        "",
        f"{COLORS['SECTION']}1. The tape{Style.RESET_ALL} contains both input strings separated by a {COLORS['SEPARATOR']}#{Style.RESET_ALL} symbol",
        f"{COLORS['SECTION']}2. The head{Style.RESET_ALL} reads and writes symbols as it moves left and right",
        f"{COLORS['SECTION']}3. States{Style.RESET_ALL} determine what action to take based on the current symbol",
        "",
        f"The machine marks characters in the first string with {COLORS['PROCESSED']}*{Style.RESET_ALL} and",
        f"corresponding matches in the second string with {COLORS['MATCHED']}X{Style.RESET_ALL}",
        "",
        "If all characters match, the strings are anagrams!"
    ]
    
    for line in explanations:
        animate_text(line)
        time.sleep(ANIMATION_SPEED)
    
    print("\nPress Enter to continue...")
    input()

def check_anagram(string1, string2, case_sensitive=True, animation_speed=ANIMATION_SPEED, show_steps=True):
    # check if two strings are anagrams using the turing machine
    clear_screen()
    print_header("TURING MACHINE ANAGRAM CHECKER")
    
    print(f"{COLORS['HEADER']}Input:{Style.RESET_ALL}")
    print(f"String 1: {COLORS['SUCCESS']}{string1}{Style.RESET_ALL}")
    print(f"String 2: {COLORS['SUCCESS']}{string2}{Style.RESET_ALL}")
    print(f"Case Sensitive: {COLORS['SECTION']}{case_sensitive}{Style.RESET_ALL}\n")
    
    if not case_sensitive:
        string1 = string1.lower()
        string2 = string2.lower()

    input_string = string1 + "#" + string2
    print(f"{COLORS['HEADER']}Combined Input:{Style.RESET_ALL} {COLORS['TEXT']}{string1}{COLORS['SEPARATOR']}#{Style.RESET_ALL}{COLORS['TEXT']}{string2}{Style.RESET_ALL}")
    
    print_section("STARTING TURING MACHINE EXECUTION")
    
    tm = TuringMachine(input_string)
    result = tm.run()
    
    if not show_steps:
        print_section("EXECUTION COMPLETE")
        if result['accepted']:
            print(f"\n{COLORS['SUCCESS']}✓ SUCCESS: '{string1}' and '{string2}' are anagrams!{Style.RESET_ALL}")
        else:
            print(f"\n{COLORS['ERROR']}✗ FAIL: '{string1}' and '{string2}' are NOT anagrams.{Style.RESET_ALL}")
        return
    
    # show animated execution log
    step_count = 0
    current_state = ""
    
    for i, step in enumerate(result['steps_log']):
        if i % 4 == 0 and i > 0:  # Group by steps (4 lines per step)
            step_count += 1
            
            if step_count > 3:  # After a few steps, ask user if they want to continue or skip to end
                print(f"\n{COLORS['SECTION']}Continue step by step? (y/n/q - yes/skip to end/quit): {Style.RESET_ALL}", end="")
                choice = input().lower()
                if choice == 'q':
                    clear_screen()
                    print(f"{COLORS['ERROR']}Execution canceled by user{Style.RESET_ALL}")
                    return
                elif choice == 'n':
                    break  # Skip to result
                clear_screen()
                print_header("TURING MACHINE EXECUTION")
                
        if step.startswith("State:"):
            # extract and color the state info
            parts = step.split(", Description: ")
            state = parts[0].replace("State: ", "")
            description = parts[1] if len(parts) > 1 else ""
            
            time.sleep(animation_speed)
            print(f"{COLORS['HEADER']}Step {step_count + 1} | State: {COLORS['STATE']}{state}{Style.RESET_ALL}")
            print(f"{COLORS['TEXT']}{description}{Style.RESET_ALL}")
        elif step.startswith("Tape:"):
            # the tape is handled separately
            pass
        elif step.startswith("Head:"):
            # head is handled with the tape
            pass
        elif step.startswith("-"):
            # show tape and head position from previous steps
            if i >= 2:
                tape = result['steps_log'][i-2].replace("Tape: ", "")
                head = result['steps_log'][i-1].replace("Head: ", "")
                head_pos = head.find("^")
                
                # display formatted tape
                formatted_tape = format_tape_display(tape, head_pos)
                time.sleep(animation_speed)
                print(f"{COLORS['HEADER']}Tape: {formatted_tape[0]}")
                print(f"{COLORS['HEADER']}Head: {formatted_tape[1]}{Style.RESET_ALL}")
                print()

    # show final state with animation
    print_section("FINAL RESULT")
    time.sleep(animation_speed * 2)
    
    if result['accepted']:
        animate_text(f"The Turing Machine ACCEPTED: The strings are anagrams!", COLORS["SUCCESS"])
    else:
        animate_text(f"The Turing Machine REJECTED: The strings are not anagrams.", COLORS["ERROR"])
    
    # display visual representation of the result
    time.sleep(animation_speed * 3)
    if result['accepted']:
        for i in range(3):
            sys.stdout.write('\r' + COLORS["SUCCESS"] + "✓ SUCCESS: ANAGRAMS CONFIRMED!" + " "*20 + Style.RESET_ALL)
            sys.stdout.flush()
            time.sleep(0.3)
            sys.stdout.write('\r' + COLORS["SUCCESS"] + "✓ SUCCESS: ANAGRAMS CONFIRMED!" + " "*20 + Style.RESET_ALL)
            sys.stdout.flush()
            time.sleep(0.3)
    else:
        sys.stdout.write('\r' + COLORS["ERROR"] + "✗ NOT ANAGRAMS" + " "*20 + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(0.6)
    
    print("\n\nPress Enter to continue...")
    input()

def run_terminal_mode():
    # argument parsing using positional arguments
    parser = argparse.ArgumentParser(description='Turing Machine Anagram Checker - Terminal Mode')
    parser.add_argument('string1', nargs='?', help='First string to check')
    parser.add_argument('string2', nargs='?', help='Second string to check')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='Perform case-sensitive comparison')
    parser.add_argument('-f', '--fast', action='store_true', help='Skip animation and show only the result')
    parser.add_argument('-e', '--explain', action='store_true', help='Show explanation of how Turing Machines work')
    args = parser.parse_args()
    
    if args.explain:
        show_turing_machine_explanation()
    
    if args.string1 and args.string2:
        check_anagram(args.string1, args.string2, args.case_sensitive, 
                      animation_speed=0 if args.fast else ANIMATION_SPEED,
                      show_steps=not args.fast)
    else:
        while True:
            clear_screen()
            # interactive mode with improved UI
            print_header("TURING MACHINE ANAGRAM CHECKER")
            print(f"{COLORS['HEADER']}This program simulates a Turing Machine to check if two strings are anagrams.{Style.RESET_ALL}")
            print(f"{COLORS['HEADER']}An anagram is a word or phrase formed by rearranging the letters of another.{Style.RESET_ALL}\n")
            
            print(f"{COLORS['SUCCESS']}[1]{Style.RESET_ALL} Check if two strings are anagrams")
            print(f"{COLORS['SUCCESS']}[2]{Style.RESET_ALL} Learn how Turing Machines work")
            print(f"{COLORS['SUCCESS']}[3]{Style.RESET_ALL} Exit")
            
            choice = input(f"\n{COLORS['SECTION']}Enter your choice (1-3): {Style.RESET_ALL}")
            
            if choice == '1':
                string1 = input(f"{COLORS['SECTION']}Enter first string: {Style.RESET_ALL}")
                string2 = input(f"{COLORS['SECTION']}Enter second string: {Style.RESET_ALL}")
                case_sensitive = input(f"{COLORS['SECTION']}Case sensitive? (y/n): {Style.RESET_ALL}").lower() == 'y'
                
                check_anagram(string1, string2, case_sensitive, 
                             animation_speed=ANIMATION_SPEED, 
                             show_steps=True)
            
            elif choice == '2':
                show_turing_machine_explanation()
            
            elif choice == '3':
                clear_screen()
                print(f"{COLORS['HEADER']}Thank you for using the Turing Machine Anagram Checker!{Style.RESET_ALL}")
                sys.exit(0)

if __name__ == '__main__':
    try:
        run_terminal_mode()
    except KeyboardInterrupt:
        print(f"\n{COLORS['ERROR']}Program terminated by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{COLORS['ERROR']}Error: {str(e)}{Style.RESET_ALL}")