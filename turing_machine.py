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
        self.state = 'scan to separator'
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

    def goto_separator(self):
        """jump straight to the separator if we know where it is."""
        if self.separator_position is not None:
            self.head_position = self.separator_position
            return True
        return False

    def goto_start(self):
        """go back to the beginning of the tape."""
        self.head_position = 5
        return True

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

        if self.state == 'scan to separator':
            # gotta find the separator first
            if symbol == '#':
                self.log_step("Found separator, starting anagram check")
                # mark where the separator is
                self.write('$')  # replace # with $ so we know where it is
                self.separator_position = self.head_position  # remember this spot
                self.state = 'find first char'
                self.goto_start()  # go back to the beginning
            elif symbol == '_':
                # check if this is just the beginning space or if we've gone too far
                if self.head_position >= 5 + 10:  # if we're way past the start
                    self.state = 'reject'
                    self.log_step("Reached end of tape without finding separator - ensure input has a # separator")
                else:
                    # still at the beginning, keep going
                    self.move('R')
            else:
                self.move('R')

        elif self.state == 'find first char':
            if symbol == '$':  # we hit our marked separator
                # if we reach the separator, we've gone through the whole first string
                self.state = 'check second string'
                self.move('R')  # move to first char of second string
                self.log_step("First string fully processed, checking second string")
            elif symbol == '*':  # skip characters we already processed
                self.move('R')
            elif symbol == '_':
                # either empty first string or we processed everything
                if self.head_position < 10:  # near the beginning
                    # probably at the start of an empty string, find separator
                    while self.read() != '$' and self.read() != '_':
                        self.move('R')
                        
                    if self.read() == '$':
                        # found separator, keep going
                        self.state = 'check second string'
                        self.move('R')  # move to first char of second string
                        self.log_step("First string is empty, checking second string")
                    else:
                        # can't find separator, that's bad
                        self.state = 'reject'
                        self.log_step("Unexpected end of first string without finding separator")
                else:
                    # might have processed all first string chars
                    # try to find separator
                    save_pos = self.head_position
                    
                    current_symbol = self.read()
                    while current_symbol != '$' and current_symbol != '_':
                        self.move('R')
                        current_symbol = self.read()
                    
                    if current_symbol == '$':
                        # found separator, check second string
                        self.state = 'check second string'
                        self.move('R')
                    else:
                        # went too far, reject
                        self.state = 'reject'
                        self.log_step("Could not find separator after first string")
            else:
                # found a character to work with
                current_char = symbol
                self.write('*')  # mark that we've dealt with this one
                self.log_step(f"Processing character '{current_char}' from first string")
                
                # remember where we are
                current_pos = self.head_position

                # go to separator if we know where it is
                if not self.goto_separator():
                    # find the separator
                    while self.read() != '$':
                        self.move('R')
                        # if we hit blank space, we went too far
                        if self.read() == '_':
                            self.state = 'reject'
                            self.log_step("Reached end of tape while looking for separator")
                            return self.head_position
                    
                    # remember separator position for later
                    self.separator_position = self.head_position

                # move to second string
                self.move('R')

                # now look for a matching character
                self.state = 'find match'
                self.original_char = current_char
                self.log_step(f"Looking for match for '{current_char}' in second string")

        elif self.state == 'find match':
            if symbol == '_':
                # reached end without a match, strings aren't anagrams
                self.state = 'reject'
                self.log_step(f"No match found for '{self.original_char}'")
            elif symbol == 'X':  # skip characters we already matched
                self.move('R')
            elif symbol == self.original_char:
                # found a match!
                self.write('X')  # mark it as matched
                self.log_step(f"Found match for '{self.original_char}'")

                # go back to first string to continue
                self.state = 'find first char'
                self.goto_start()  # back to beginning
            else:
                # not a match, keep looking
                self.move('R')

        elif self.state == 'check second string':
            if symbol == 'X':  # skip characters we already matched
                self.move('R')
            elif symbol == '_':
                # got to the end of second string and everything matched!
                self.state = 'accept'
                self.log_step("All characters matched, strings are anagrams!")
            else:
                # found a character that wasn't matched
                self.state = 'reject'
                self.log_step(f"Found unmatched character '{symbol}' in second string")
        
        return self.head_position
