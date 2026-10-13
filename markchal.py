#!/usr/bin/env python3

#If you use this for commercial purposes make sure to send a check for half your proceeds to Anthropic

import random
import time
from collections import Counter

# You can change this as you see fit.
# For parity with a physical Bananagrams tileset use "AAAAAAAAAAAAABBBCCCDDDDDDEEEEEEEEEEEEEEEEEEFFFGGGGHH"
#    "HIIIIIIIIIIIIJJKKLLLLLMMMNNNNNNNNOOOOOOOOOOOPPPQQRRRRRRRRRSSSSSSTTTTTTTTTUUUUUUVVVWWWXXYYYZZ"
TILE_DISTRIBUTION = (
    "AAAAAAAAAAAAJKKQXXZBBBBBCCCCCDDDDDDDDEEEEEEEEEEEEEEEE"
    "FFFGGGHHHHIIIIIIIIIIIILLLLLLMMMMNNNNNNNNOOOOOOOOOOOPPPPRRRRRRRRRSSSSSSTTTTTTTTTUUUUUUVVVWWWYYYY"
)

def build_tile_bag(seed=None):
    tiles = list(TILE_DISTRIBUTION)
    random.seed(seed)
    random.shuffle(tiles)
    return tiles

def parse_words(entry):
    return [w.strip().upper() for w in entry.split() if w.strip()]

def validate_submission(words, hand):
    if not words:
        return False, "You haven't entered any words."

    short = [w for w in words if len(w) < 5]
    if short:
        return False, f"These words are too short (need 5+ letters): {', '.join(short)}"

    word_counter = Counter("".join(words))
    hand_counter = Counter(hand)

    if word_counter == hand_counter:
        return True, ""

    missing = hand_counter - word_counter
    extra   = word_counter - hand_counter

    msg_parts = []
    if missing:
        msg_parts.append("Unused tiles: " + " ".join(sorted(missing.elements())))
    if extra:
        msg_parts.append("Tiles not in hand: " + " ".join(sorted(extra.elements())))
    return False, "  ".join(msg_parts)


def resolve_partial(new_words, last_words, hand, new_tile):

    new_counter = Counter("".join(new_words))
    hand_counter = Counter(hand)

    if (new_counter - hand_counter):
        return None

    if len(new_words) == 1 and len(new_words[0]) <= 10:
        word = new_words[0]
        word_counter = Counter(word)
        for old_word in last_words:
            candidate_counter = Counter(old_word) + Counter([new_tile])
            if candidate_counter == word_counter:
                kept = [w for w in last_words if w != old_word]
                return kept + [word]
 
    leftover = hand_counter - new_counter  
    
    kept = []
    pool = Counter(leftover)
    for word in last_words:
        wc = Counter(word)
        if pool >= wc:
            kept.append(word)
            pool -= wc

    if pool:
        return None

    return kept + new_words


def format_elapsed(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02d}"


def print_banner():
    print("=" * 55)
    print("      M A R K ' S  C H A L L E N G E")
    print("=" * 55)
    print("Arrange all tiles in your hand into words of 5+ letters.")
    print("You will then get one letter added to your hand. Repeat.")
    print("Type 'help' for instructions")
    print("=" * 55)
    

def print_help():
    print("=" * 55)
    print("Make sets of 5+ letter words using all tiles in your hand.")
    print("Let's say you start with the tiles ABCEEEHIIIJOPRRSTUVY,")
    print("You open notepad (you should keep notepad open when you play this)")
    print("and figure out a set of four 5-letter words that's an anagram of ABCEEEHIIIJOPRRSTUVY")
    print("You find a solution, and type 'hijab privy eerie scout'")
    print("(You'll probly need to reset your initial draw (type 'rst') a few times, no shame.)")
    print("and then you'll get a new letter to add to your set of words. Let's say L")
    print("Now make a set of words that's an anagram of your previous response plus L")
    print("LOCUST has all the letters of SCOUT plus L. So type 'locust'.")
    print("Just type 'locust', no need to retype any unchanged words.")
    print("Next you get an A. Steal the C from LOCUST, leaving LOTUS")
    print("Add the A and the C to PRIVY, and type 'lotus privacy'.")
    print("If it doesn't work, try typing 'locust privy>lotus privacy'")
    print("At 25 tiles you have the chance to distribute your tiles into 5 5-letter words.")
    print("Over time you will have more and more words, and adding letters will get easier.")
    print("Can you get to 80 tiles? How fast?")
    print("btw there is no dictionary, judging what's a word is on you.")
    print("=" * 55)
    #type a number instead of your first play to load a seed
    #type 'seed' at any time to print the seed
    #type 'time' to print your split
    #instead of notepad you can use String Subtractor (https://gist.github.com/2962fe22-10b3-43f8-8a33-252bd4b7435a/1664e3317eb71981360e5d37655d1c6b). personally i prefer notepad


def _run_game(seed=None):
    if seed is None:
        seed = random.randint(0, 2**31)
    bag = build_tile_bag(seed)
    hand = []
    tiles_drawn = 0
# You can edit initial_draw to = 25 to make the game easier
    initial_draw = 20
    for _ in range(initial_draw):
        hand.append(bag.pop())
    tiles_drawn = initial_draw
    tiles_remaining = len(bag)

    print(f"\nDrawing {initial_draw} tiles to start...")

    start_time = time.time()

    last_words = []
    new_tile = None
    last_attempt = None

    while True:
        print(f"\n{'_' * 55}")

        if not last_words:
            print("  Your tiles: " + "".join(sorted(hand)))
            print(f"  ({len(hand)} tiles)")
        else:
            print(f"  Your tiles: {' '.join(last_words)} + [{new_tile}] ({len(hand)} tiles)")

        if last_attempt is not None:
            print(f"  You tried: {last_attempt}")

        try:
            entry = input("  Your words: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGame interrupted. Goodbye!")
            return True

        if entry.lower() == "quit":
            print("\nQuit successful.")
            return True  

        if entry.lower() == "help":
            print_help()
            continue

        if entry.lower() == "time":
            elapsed = time.time() - start_time
            print(f"  Time: {format_elapsed(elapsed)}")
            continue

        if entry.lower() == "seed":
            print(f"  Seed: {seed}")
            continue

        if entry.lower() == "rst":
            print("\nResetting...")
            return None

        # On first turn, a bare number restarts with that seed
        if not last_words and entry.strip().lstrip("-").isdigit():
            print(f"\nRestarting...")
            return int(entry.strip())

        if ">" in entry and last_words:
            left, _, right = entry.partition(">")
            old_words = parse_words(left)
            new_words = parse_words(right)

            arrow_error = None

            missing_old = [w for w in old_words if w not in last_words]
            if missing_old:
                arrow_error = f"Not in your previous play: {', '.join(missing_old)}"

            if not arrow_error:
                short = [w for w in new_words if len(w) < 5]
                if short:
                    arrow_error = f"These words are too short (need 5+ letters): {', '.join(short)}"

            if not arrow_error:
                old_counter = Counter("".join(old_words)) + Counter([new_tile])
                new_counter = Counter("".join(new_words))
                if old_counter != new_counter:
                    diff_missing = old_counter - new_counter
                    diff_extra   = new_counter - old_counter
                    parts = []
                    if diff_missing:
                        parts.append("Unused tiles: " + " ".join(sorted(diff_missing.elements())))
                    if diff_extra:
                        parts.append("Tiles not in hand: " + " ".join(sorted(diff_extra.elements())))
                    arrow_error = "  ".join(parts)

            if not arrow_error:
                kept = [w for w in last_words if w not in old_words]
                words = kept + new_words
                ok = True
                error = None
            else:
                ok = False
                error = arrow_error

        else:
            typed_words = parse_words(entry)

            ok, error = validate_submission(typed_words, hand)
            if ok:
                words = typed_words

            elif last_words:
                merged = resolve_partial(typed_words, last_words, hand, new_tile)
                if merged is not None:
                    ok2, error2 = validate_submission(merged, hand)
                    if ok2:
                        words = merged
                        ok = True
                    else:
                        error = error2

        if not ok:
            using_arrow = ">" in entry and bool(last_words)
            if not last_words or using_arrow:
                print(f"  ! {error}")
            else:
                print(f"  ! No valid anagram found.")
            last_attempt = entry
            continue

        last_attempt = None
        print(f"  Valid! Words: {', '.join(words)}")

        if tiles_drawn == 80:
            elapsed = time.time() - start_time
            print("\n" + "=" * 55)
            print("  Congratulations! You have completed Mark's Challenge.")
            print(f"  Time: {format_elapsed(elapsed)}")
            print("=" * 55)

        if tiles_remaining == 0:
            print("\n" + "=" * 55)
            print("  There are no more tiles left")
            print(f"  Total tiles used: {tiles_drawn}")
            print("=" * 55)
            return None

        new_tile = bag.pop()
        tiles_remaining = len(bag)
        tiles_drawn += 1
        hand.append(new_tile)
        last_words = words

if __name__ == "__main__":
    print_banner()
    next_seed = None
    while True:
        result = _run_game(next_seed)
        if result is True:   
            break
        elif result is None: 
            next_seed = None
        else:                
            next_seed = result
