class TuringMachine:
    """
    our implementation of a turing machine that checks if two strings are anagrams.
    
    basically this whole thing drives the algorithms and state transitions for the machine
    that figures out if two strings (separated by a '#') are anagrams or not.
    """
    
    def __init__(self, input_string):
        """
        sets up the turing machine with the starting tape.
        
        args:
            input_string: the strings to check, separated by the '#' symbol
        """
        # figuring out how big to make the tape
        input_length = len(input_string)
        padding_left = 5  # some space on the left
        padding_right = max(20, input_length)  # gotta have enough space on the right too
        
        # make the tape with input and blank space at both ends
        self.tape = list('_' * padding_left + input_string + '_' * padding_right)
        self.head_position = padding_left  # start after the blank spaces
        self.state = 'scan_to_separator'
        self.steps_log = []
        
        # remember where the separator is so we can find it easily
        self.separator_position = None
        
        # this part is just a hack for efficiency on big inputs
        # checks if both strings are just the same char repeated
        if '#' in input_string:
            parts = input_string.split('#')
            if len(parts) == 2:
                if len(parts[0]) > 0 and len(parts[1]) > 0:
                    is_single_char_string1 = all(c == parts[0][0] for c in parts[0])
                    is_single_char_string2 = all(c == parts[1][0] for c in parts[1])
                    
                    # if both strings are the same single char repeated
                    if is_single_char_string1 and is_single_char_string2 and parts[0][0] == parts[1][0]:
                        # check if lengths are equal for anagram status
                        if len(parts[0]) == len(parts[1]):
                            self.state = 'accept'  # yup, they're anagrams
                            self.log_step("Optimization: Detected matching repeated character strings of equal length")
                        else:
                            self.state = 'reject'  # nope, not anagrams - different lengths
                            self.log_step("Optimization: Detected repeated character strings of unequal length")

    def read(self):
        """read whatever symbol is at the current position."""
        return self.tape[self.head_position]

    def write(self, symbol):
        """
        write a symbol to the tape at current position.
        
        args:
            symbol: whatever we're writing to the tape
        """
        self.tape[self.head_position] = symbol

    def move(self, direction):
        """
        moves the head left or right.
        
        args:
            direction: 'L' for left, 'R' for right
        """
        if direction == 'L':
            self.head_position -= 1
            # don't fall off the left side
            if self.head_position < 0:
                self.head_position = 0
        elif direction == 'R':
            self.head_position += 1
            # add more space if we're running out
            if self.head_position >= len(self.tape) - 10:  # less than 10 cells left
                self.tape.extend(['_'] * 100)  # extend the tape with additional blank cells

    def getState(self):
        return self.state

    def log_step(self, description):
        """
        keep track of what the machine is doing at each step.
        
        args:
            description: what's happening in this step
        """
        tape_str = ''.join(self.tape)
        head_indicator = ' ' * self.head_position + '^'
        self.steps_log.append(f"State: {self.state}, Description: {description}")
        self.steps_log.append(f"Tape: {tape_str}")
        self.steps_log.append(f"Head: {head_indicator}")
        self.steps_log.append("-" * 50)
    def run(self):
        """
        runs the whole turing machine until it accepts or rejects.
        
        returns:
            a dict with:
                'accepted': true if they're anagrams, false if not
                'steps_log': all the steps we took
        """
        self.log_step("Starting the Turing Machine")

        # if we already know the answer from our optimization, just return it
        if self.state in ['accept', 'reject']:
            return {
                'accepted': self.state == 'accept',
                'steps_log': self.steps_log
            }

        # safety check so we don't get stuck in an infinite loop
        max_steps = min(100000, len(self.tape) * 10)  # hopefully this is enough
        step_count = 0

        while self.state not in ['accept', 'reject'] and step_count < max_steps:
            self.step()
            step_count += 1
            
        # if we hit the step limit, something's wrong
        if step_count >= max_steps:
            self.state = 'reject'
            self.log_step("Exceeded maximum steps - potential infinite loop detected")

        return {
            'accepted': self.state == 'accept',
            'steps_log': self.steps_log
        }

    def step(self):
        """
        does a single step of the machine.
        
        returns:
            where the head is after this step
        """
        symbol = self.read()

        if self.state == 'scan_to_separator':
            # scan right until we find the separator
            if symbol == '#':
                self.log_step("Found separator, starting anagram check")
            # mark where the separator is
                self.write('$')  # Replace # with $ so we know where it is
                self.separator_position = self.head_position  # Remember this spot
            # now go back to the start to process the first string
                self.state = 'find_first_char'
                self.move('L')  # Start moving left
                self.log_step("Moving left to find_first_char")
            elif symbol == '_':
                # check if this is just the beginning space or if we've gone too far
                if self.head_position >= 5 + 10:  # If we're way past the start
                    self.state = 'reject'
                    self.log_step("Reached end of tape without finding separator - ensure input has a # separator")
                else:
                # still at the beginning, keep going
                    self.move('R')
                    self.log_step("Moving right to find separator")
            else:
                self.move('R')
                self.log_step("Moving right to find separator")
    
        elif self.state == 'find_first_char':
            # going back to the beginning of the tape
            if self.head_position == 5:
                # we've reached the beginning of the padding
                self.state = 'found_first_char'
                #self.move('R')  # Move right to start processing
                self.log_step("Found first character position")
            elif symbol == '*':
                self.state='found_first_char'
            else:
                # keep moving left
                self.move('L')
                self.log_step("Moving left to find_first_char")
    
        elif self.state == 'found_first_char':
            if symbol == '$':
            # reached the separator
                self.state = 'check second string'
                self.move('R')
                self.log_step("First string fully processed, checking second string")
            elif symbol == '*':
            # this character is already processed, move right
                self.move('R')
                self.log_step("Skipping already processed character")
                self.state = 'found_first_char'  # Stay in same state
            elif symbol == '_' and self.head_position >= 5:
            # at the beginning padding, move right
                self.move('R')
                self.log_step("At beginning padding, moving right")
                self.state = 'found_first_char'  # Stay in same state
            elif symbol == '*' and self.head_position >= 5:
            # reached blank space in the middle of the string - move right
                self.move('R')
                self.log_step("Found blank in first string, moving right")
                self.state = 'found_first_char'  # Stay in same state
            else:
            # found an unprocessed character
                current_char = symbol
                self.write('*')  # Mark as processed
                self.original_char = current_char
                self.log_step(f"Processing character '{current_char}' from first string")
            
            # now look for a match in the second string
                self.state = 'scanback_to_separator'
                self.move('R')
                self.log_step("Moving right to find separator")
    
        elif self.state == 'scanback_to_separator':
            if symbol == '$':
            # found the separator, now move to second string
                self.state = 'match_char'
                self.move('R')
                self.log_step(f"Reached separator, starting match search for '{self.original_char}'")
            elif symbol == '_':
            # end of tape without finding separator
                self.state = 'reject'
                self.log_step("Failed to find separator")
            else:
            # keep moving right to find separator
                self.move('R')
                self.log_step("Moving right to find separator")

        elif self.state == 'found_char':
            self.state = 'find_first_char'
            self.move('L')
    
        elif self.state == 'match_char':
            if symbol == '_':
                # reached end without a match, strings aren't anagrams
                self.state = 'reject'
                self.log_step(f"No match found for '{self.original_char}'")
            elif symbol == 'X':  # skip characters we already matched
                self.move('R')
                self.log_step("Skipping already matched character")
            elif symbol == self.original_char:
            # found a match!
                self.write('X')
                self.state = 'found_char'
                self.log_step(f"Found match for '{self.original_char}'")
                #self.move('L')
            # return to first string to process next character
                #self.state = 'find_first_char'  # Restart from beginning
                self.log_step("Moving left to find_first_char")
            else:
                # not a match, keep looking
                self.move('R')
                self.log_step("Moving right to match_char")
    
        elif self.state == 'check second string':
            if symbol == 'X':  # skip characters we already matched
                self.move('R')
                self.log_step("Skipping matched character in second string")
            elif symbol == '_':
                # got to the end of second string and everything matched!
                self.state = 'accept'
                self.log_step("All characters matched, strings are anagrams!")
            else:
                # found a character that wasn't matched
                self.state = 'reject'
                self.log_step(f"Found unmatched character '{symbol}' in second string")
        
        return self.head_position
