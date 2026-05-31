#!/usr/bin/env python3
import sys
import random

fortunes = [
    "Write code as if the next maintainer is a psychopath who knows where you live.",
    "Deleted code is debugged code.",
    "It's not a bug – it's an undocumented feature.",
    "To err is human, but to really foul things up you need a computer.",
    "One man's constant is another man's variable.",
    "Hardware: the parts of a computer that you can kick.",
    "Computer science is no more about computers than astronomy is about telescopes.",
    "The best thing about a boolean is even if you are wrong, you are only off by a bit.",
    "If at first you don't succeed; call it version 1.0.",
    "There are only 10 types of people in the world: Those who understand binary, and those who don't.",
    "In a world without fences and walls, who needs Gates and Windows?",
    "Programming is like sex. One mistake and you have to support it for the rest of your life.",
    "Documentation is like sex; when it's good, it's very, very good, and when it's bad, it's better than nothing.",
    "There are two ways to write error-free programs; only the third one works.",
    "Computers are good at following instructions, but not at reading your mind.",
    "Get that green!",
    "Keep committing.",
    "Code never lies, comments sometimes do.",
    "Simplicity is the soul of efficiency.",
    "Don't worry if it doesn't work right. If everything did, you'd be out of a job.",
    "Think twice, code once."
]

def main():
    max_len = None
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '-n' and i + 1 < len(args):
            try:
                max_len = int(args[i+1])
            except ValueError:
                pass
        elif arg.startswith('-sn'):
            try:
                max_len = int(arg[3:])
            except ValueError:
                pass
        elif arg == '-sn' and i + 1 < len(args):
            try:
                max_len = int(args[i+1])
            except ValueError:
                pass

    choices = fortunes
    if max_len is not None:
        choices = [f for f in fortunes if len(f) <= max_len]
        if not choices:
            choices = ["Get that green!"]

    print(random.choice(choices))

if __name__ == '__main__':
    main()
