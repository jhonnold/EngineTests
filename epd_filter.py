import os
import re
import sys
from uci_engine import Engine

W_Min = 400
W_Max = 600

def filter(testfile, output):
    def win_analysis(engine, fen, depth = 22):
        engine.ucinewgame()
        engine.set_option('UCI_ShowWDL', 'true')
        engine.position(fen)
        engine.go(depth=depth)

        w = 0

        while True:
            response = engine.readline()
            match = re.search(' wdl (\d+) (\d+) (\d+) ', response)
            if match: w = int(match.group(1));
            if response.startswith('bestmove'): break;

        return w

    engines = os.listdir("engines/")[:1]
    engine = Engine(engines[0], "engines/")

    kept = 0

    with open(output, 'w') as out:
        with open(testfile, 'r') as fens:
            for count, fen in enumerate(fens):
                w = win_analysis(engine, fen)

                if w >= W_Min and w <= W_Max:
                    kept += 1
                    out.write(fen)

                if (count+1) % 1000 == 0:
                    print(f"Kept {kept} fen(s) of {count+1}")

if __name__ == "__main__":
    filter(sys.argv[1], sys.argv[2])
