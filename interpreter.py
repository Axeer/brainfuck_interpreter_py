import sys
import time

stop = False
running = False

max_time_secs = 5 # funnyword alert!
suspend_on_debug = False

class Message:
    infinityloop = 'falling into infinity loop'
    nonepath = 'please enter a path to bf file'


class Keywords:
    debug = '#'
    comment = '!'
    keywords = None
    def __init__(self):
        self.keywords = '-+><[],.{}{}'.format(Keywords.debug, Keywords.comment)
kw = Keywords()

class Loop:
    enter_ptr = None
    start_pos = None
    end_pos = None
    #TODO if on end loop enter_ptr == outer_ptr: eto infinity loop

def exit(code = 0):
    running = False
    sys.exit(code)


def execute(file):
    global stop
    global running
    global ignore
    stop = False
    running = True
    ignore = False

    with open(file) as program:
        program_content = program.read()
        program_content = [i for i in program_content if i in kw.keywords]

    position = 0
    pointer = 0
    memory = [0]
    loop_enter_ptr = 0
    loop_enter_val = 0

    bracemap = build_bracemap(program_content)

    class Debug:
        @staticmethod
        def out():
            curmem = 0
            print("\n|{0:4}| -> |{1:4}|".format("memcell:", "contains:"))
            for memcell in memory:
                print(f"{curmem:5} {'->'} {memcell:5}")
                curmem += 1
            print(f"cur ptr: {pointer} (value: {memory[pointer]} char: '{chr(memory[pointer])}')")
            print(f"cur pos: {position}(instruction: {program_content[position-1]})")
            if suspend_on_debug: input("enter any key to continue executing...")

    time_start = time.time()

    def match(sym):
        return program_content[position] == sym and not ignore or program_content[position] == kw.comment

    def out():
        print(chr(memory[pointer]), end="")

    while position < len(program_content):

        if match(kw.comment):
            ignore = not ignore

        elif match(">"):
            pointer += 1
            if len(memory) <= pointer:
                memory.append(0)
                
        elif match("<"):
            pointer -= 1
            if pointer < 0:
                print("Range error")
                exit()

        elif match("+"):
            memory[pointer] += 1
            if memory[pointer] > 255:
                memory[pointer] = 0
                
        elif match("-"):
            memory[pointer] -= 1
            if memory[pointer] < 0:
                memory[pointer] = 255
                
        elif match("."):
            out()
            
        elif match(","):
            memory[pointer] = ord(input()[0])

        elif match("[") and memory[pointer] == 0:
            try:
                position = bracemap[position]
            except KeyError:
                print("Key Error")
                exit()

        elif match("[") and memory[pointer] != 0:
            # FIXME
            loop_enter_val = memory[pointer]
            loop_enter_ptr = pointer

        elif match("]") and memory[pointer] != 0:
            try:
                if loop_enter_val <= memory[loop_enter_ptr]:
                    print(Message.infinityloop)
                    exit()
                position = bracemap[position]
            except KeyError:
                print("Key Error")
                exit()

        elif match(kw.debug):
            Debug.out()

        if stop:
            exit()
        
        position += 1
        time_end = time.time()

        if (time_end - time_start) > max_time_secs:
            pass

    running = False
    return memory


def build_bracemap(code):
    temp = []
    bracemap = {}

    try:
        for position, command in enumerate(code):
            if command == "[": temp.append(position)
            if command == "]":
                start = temp.pop()
                bracemap[start] = position
                bracemap[position] = start
        return bracemap
    except IndexError:
        print("Parse Error")
        exit()

if __name__ == '__main__':
    try:
        bffile = sys.argv[1]
    except:
        print(Message.nonepath)
        exit()
    if bffile is not None:
        exit(execute(bffile))
