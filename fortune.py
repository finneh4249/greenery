#!/usr/bin/env python3
import sys
import random
import hashlib

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

# Vocabulary lists for programmatic generation
nouns = [
    "bug", "feature", "compiler", "database", "stack overflow", "git repository",
    "pull request", "refactoring", "documentation", "test case", "production server",
    "microservice", "AI agent", "kubernetes pod", "coffee", "psychopath", "regex",
    "monad", "callback hell", "null pointer", "merge conflict", "wrapper", "legacy system",
    "JSON payload", "cloud cost", "YAML config", "CI/CD pipeline", "unit test", "linters"
]

verbs = [
    "deploy", "debug", "refactor", "break", "fix", "optimize", "delete", "write",
    "compile", "commit", "push", "reboot", "ignore", "document", "automate",
    "over-engineer", "containerize", "deprecate"
]

adjectives = [
    "deprecated", "undocumented", "highly optimized", "spaghetti", "legacy", "flaky",
    "untested", "deterministic", "psychopathic", "serverless", "stateless", "recursive",
    "thread-safe", "compiled", "over-engineered", "elegant", "cryptic", "asynchronous"
]

templates = [
    "A {adjective} {noun} a day keeps the {noun} away.",
    "Deleted {noun} is {adjective} {noun}.",
    "It's not a {noun} - it's a {adjective} {noun}.",
    "To {verb} is human, but to really {verb} things up you need a {noun}.",
    "One {noun}'s {noun} is another {noun}'s {noun}.",
    "The best thing about a {noun} is that it's {adjective}.",
    "If at first you don't {verb}; call it {adjective} version 1.0.",
    "There are only 10 types of {noun}: those who {verb} it, and those who {verb} {noun}.",
    "Programming is like {noun}. One {adjective} mistake and you have to {verb} it for the rest of your life.",
    "Don't {verb} if it doesn't {verb} right. If everything did, you'd be out of a {noun}.",
    "Think twice, {verb} once.",
    "Write {noun} as if the next {noun} is a {noun} who knows where you {verb}.",
    "A {adjective} {noun} always {verb}s the {noun}.",
    "Never {verb} a {adjective} {noun} on a Friday afternoon.",
    "{verb} first, ask questions as {adjective} comments later.",
    "A {noun} is just a {noun} wrapped in a {adjective} {noun}."
]

def generate_fortune(rng):
    template = rng.choice(templates)
    
    # We construct dictionary of replacements dynamically
    replacements = {}
    for key, word_list in [("noun", nouns), ("verb", verbs), ("adjective", adjectives)]:
        # Count formatting occurrences of key in template
        count = template.count("{" + key + "}")
        for idx in range(count):
            replacements[f"{key}{idx if idx > 0 else ''}"] = rng.choice(word_list)
            
    # Format templates that might have multiple references
    # E.g., "{noun} ... {noun}" -> We can name them {noun} and {noun0} or similar in code,
    # but templates have standard formatting. Let's make sure each replacement placeholder gets a distinct word.
    formatted_template = template
    while "{" in formatted_template:
        for placeholder, word_list in [("{noun}", nouns), ("{verb}", verbs), ("{adjective}", adjectives)]:
            if placeholder in formatted_template:
                formatted_template = formatted_template.replace(placeholder, rng.choice(word_list), 1)
                
    return formatted_template

def main():
    max_len = None
    seed_val = None
    count = 1
    
    # Parse CLI arguments (manual parsing to preserve exact legacy option support)
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-n' and i + 1 < len(args):
            try:
                max_len = int(args[i+1])
                i += 2
                continue
            except ValueError:
                pass
        elif arg == '-sn' and i + 1 < len(args):
            try:
                max_len = int(args[i+1])
                i += 2
                continue
            except ValueError:
                pass
        elif arg.startswith('-sn'):
            try:
                max_len = int(arg[3:])
                i += 1
                continue
            except ValueError:
                pass
        elif (arg == '-s' or arg == '--seed') and i + 1 < len(args):
            seed_val = args[i+1]
            i += 2
            continue
        elif (arg == '-c' or arg == '--count') and i + 1 < len(args):
            try:
                count = int(args[i+1])
                i += 2
                continue
            except ValueError:
                pass
        
        i += 1

    # Initialize deterministic or non-deterministic RNG
    rng = random.Random()
    if seed_val is not None:
        # Generate a seed value hash so strings work perfectly
        seed_hash = hashlib.sha256(seed_val.encode('utf-8')).digest()
        rng.seed(seed_hash)

    # Let's combine static fortunes and generated fortunes for maximum diversity
    all_fortunes_generator = lambda: rng.choice([True, False])
    
    for _ in range(count):
        # We try to get/generate a fortune satisfying max_len
        attempts = 0
        while attempts < 100:
            # 50% chance of choosing a static fortune, 50% of generating one
            if all_fortunes_generator():
                choice = rng.choice(fortunes)
            else:
                choice = generate_fortune(rng)
                
            if max_len is None or len(choice) <= max_len:
                print(choice)
                break
            attempts += 1
        else:
            # Fallback if no choice fits max_len
            print("Get that green!")

if __name__ == '__main__':
    main()
