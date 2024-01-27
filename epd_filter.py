import os, re, sys, concurrent.futures
from multiprocessing import freeze_support, cpu_count
from uci_engine import Engine
from tqdm import tqdm

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

W_Min = 400
W_Max = 600

class Filterer:
    def __init__(self):
        self.engine = os.listdir("engines/")[0]

    def filter(self, fens):
        result_fens = []

        engine = Engine(self.engine, "engines/")
        engine.set_option('UCI_ShowWDL', 'true')

        for fen in fens:
            engine.ucinewgame()
            engine.position(fen)
            engine.go(depth=22)

            w = 0

            while True:
                response = engine.readline()
                match = re.search(' wdl (\d+) (\d+) (\d+) ', response)
                if match: w = int(match.group(1));
                if response.startswith('bestmove'): break;

            if w >= W_Min and w <= W_Max:
                result_fens.append(fen)

        engine.quit()

        return result_fens

if __name__ == "__main__":
    freeze_support()

    fens = []
    with open(sys.argv[1]) as f:
        for line in f:
            fens.append(line)

    filter = Filterer()

    workers = cpu_count()
    num_fens = len(fens)

    print(f"Loaded {num_fens} fen(s)")

    fenschunked = list(chunks(fens, 256))

    res = []
    futures = []

    with tqdm(total=len(fenschunked), smoothing=0, miniters=1) as pbar:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as e:
            for entry in fenschunked:
                futures.append(e.submit(filter.filter, entry))

            for future in concurrent.futures.as_completed(futures):
                pbar.update(1)
                res += future.result()

    with open(sys.argv[2], 'w') as f:
        f.writelines(res)
