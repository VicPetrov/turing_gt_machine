"""
X > Y Turing Machine
in
Python 3.9.6
accepts Unary Encoded unsgined integers
writes 0 or 1 at the end of tape if X > Y
"""

from itertools import repeat


class TuringMachine:
    ####    Turing machine is a stateful automatic system design
    #### with a hardware tape and write head
    ### and a table of rules modulating its behaviour;
    state: str
    write_head: int
    tape_list: list[int]

    def __init__(self, state: str, write_head: int, tape_list: list[int]):
        self.state = state
        self.write_head = write_head
        self.tape_list = tape_list

    def __iter__(self):
        return iter(self.update_machine, True)

    def update_machine(self):
        # We go in the right direction first, marking first element of the input sequence with a 0
        # We skip both Unary Encoded numbers and then go in the opposite direction accumulating right-hand side argument
        # in [A]ccumulation state (a%d)
        # then we pass the accumulated value and decrement for each significant bit of the left-hand side argument
        # all-the-while keeping track of it in our [D]ecrement state (d%d)
        # If state machine reaches state `d0` before it finds our mark in the beginning of sequence `X > Y` statement is
        # considered TRUE and we attempt to restore initial values and write 1;
        # If the opposite holds true we reach the end of inut sequence and deem `X > Y` - `False`, restore values, and write 0
        # NOTE: Each update consists of:
        #   - state evaluation
        #   - write
        #   - shift of the `write_head` referred to as MOVE
        # NOTE: left-hand side and right-hand side from here on out will be referred to as lhs and rhs, respectively.
        if self.state == "q1":
            ####? STATE -- Shift to "L-state" to skip all of lhs argument bits until 0
            bit_read = self.tape_list[self.write_head]
            self.state = "".join(["l", str(bit_read)])  # l%d formatted string
            #! WRITE -- mark the beginning of unary encoded sequence with 0
            self.tape_list[self.write_head] = 0
            # MOVE -- Right
            self.write_head += 1

        elif self.state == "a0":
            # a for accumulator state
            # ? state - add up all the itty-bitties until end of rhs argument.
            bit_read = self.tape_list[self.write_head]
            self.state = "".join([self.state[0], str(bit_read + int(self.state[1:]))])
            #! Write - Unchanged
            # Move -- Left
            self.write_head -= 1

        elif self.state == "r0":
            # ? STATE -- Shift to "a-state"
            self.state = "a0"
            #! Write - Unchanged
            # Move -- Still
            self.write_head = self.write_head

        elif self.state == "l0":
            ####? STATE -- shift to "r-state" to skip all of rhs argument bits this time.
            bit_read = self.tape_list[self.write_head]
            self.state = "".join(["r", str(bit_read)])
            #! WRITE -- Unchanged
            # MOVE -- Right
            self.write_head += bit_read

        elif self.state == "d0":
            ####? State -- shift to "ts-state" to restore input data in case of X>Y == True
            bit_read = self.tape_list[self.write_head]
            self.state = "ts"
            #! Write -- Unchaged
            # Move -- Left
            self.write_head -= 1

        elif self.state.startswith("l"):
            # ? state check for 0
            bit_read = self.tape_list[self.write_head]
            self.state = "".join(["l", str(bit_read)])  # -- l%d
            #! WRITE -- Unchanged
            # MOVE -- Right
            self.write_head += 1

        elif self.state.startswith("r"):
            # ? state check for 0
            bit_read = self.tape_list[self.write_head]
            self.state = "".join(["r", str(bit_read)])  # -- r%d
            #! WRITE -- Unchanged
            # MOVE -- Right
            self.write_head += bit_read

        elif self.state.startswith("a"):
            # a for accumulator state
            # ? state - add up all the itty-bitties until end of rhs argument.
            bit_read = self.tape_list[self.write_head]
            if bit_read != 0:
                self.state = "".join(
                    [self.state[0], str(bit_read + int(self.state[1:]))]
                )
            else:
                self.state = "".join(["d", self.state[1:]])
            #! Write - Unchanged
            # Move -- Left
            self.write_head -= 1

        elif self.state.startswith("d"):
            # d for decrement - state
            # ? state - decrease until either state[1] hits 0
            # ? or bit read is 0 (the beginning of input we marked in q1)
            bit_read = self.tape_list[self.write_head]

            if bit_read != 0:
                self.state = "".join(
                    [self.state[0], str(int(self.state[1:]) - bit_read)]
                )
            else:
                # if `bit_read == 0` shift to "False, lhs argument"-state
                self.state = "fl"

            #! Write - Unchanged
            # Move - left
            self.write_head -= 1

        elif self.state == "ts":
            # [T]rue, re[S]tore
            # ? state - OR 1 all until left-end of lhs to restore original value;
            bit_read = self.tape_list[self.write_head]
            if bit_read == 0:
                self.state = "tl"
            #! Write -- mut `bit_read | 1`
            # ? assert (0 | 1) == 1 and (1 | 1) == 1
            self.tape_list[self.write_head] |= 1
            # Move -- Left if `bit_read` != 0 else -- Still
            self.write_head = self.write_head - 1 if bit_read != 0 else self.write_head

        elif self.state == "fl":
            # False, lhs argument
            # ? State - skip to 0 then False, rhs
            bit_read = self.tape_list[self.write_head + 1]
            if bit_read == 0:
                self.state = "fr"  # -- false, rhs
            #! Write -- Unchanged
            # Move -- Right
            self.write_head += 1

        elif self.state == "fr":
            # False, rhs argument
            # ? State - same as "tl" then "w" for write-state.
            bit_read = self.tape_list[self.write_head - 1]
            if bit_read == 0:
                self.state = "wf"  # -- write False
            #! Write -- Unchanged
            # Move -- Right
            self.write_head += 1

        elif self.state == "tl":
            # True, skip to end of lhs argument
            # ? State - skip to 0 then True, rhs
            bit_read = self.tape_list[self.write_head]
            if bit_read == 0:
                self.state = "tr"  # -- True, rhs
            #! Write -- Unchanged
            # Move -- Right
            self.write_head += 1

        elif self.state == "tr":
            # True, rhs argument
            # ? State - same as "tl" then "w" for write-state.
            bit_read = self.tape_list[self.write_head - 1]
            if bit_read == 0:
                self.state = "wt"  # -- write True
            #! Write -- Unchanged
            # Move -- Right
            self.write_head += 1

        elif self.state.startswith("w"):
            # ? state - shift state to END STATE (qq)
            prev_state = self.state
            self.state = "qq"
            #! Write -- 1
            self.tape_list.append(1 if prev_state[1] == "t" else 0)
            # Move -- still
            self.write_head = self.write_head

        elif self.state == "qq":
            return True

        return False


if __name__ == "__main__":
    ## input X Y
    # ? Split input string and convert it to integers
    input_tape: map[int] = map(int, input().split())
    ## Unary Encoding
    # ? e.g.:
    # ? ```
    # ?      5   ==> 111110;
    # ?      10  ==> 11111111110.
    # ? ```
    unary_encoded_tape: list[int] = list()
    for number in input_tape:
        for ones in repeat(1, number):
            unary_encoded_tape.append(ones)
        unary_encoded_tape.append(0)  # Terminating zero

    ## Turing Machine __init__
    gt_machine: TuringMachine = TuringMachine(
        state="q1",  # - initial state
        write_head=0,  # - start of sequence
        tape_list=unary_encoded_tape,  # - our input
    )

    [cycle for cycle in gt_machine]  # Cycle machine from q1 until end-state (qq)

    print("X > Y is ", end="")
    print(repr(gt_machine.tape_list.pop() == 1))
