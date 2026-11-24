import argparse
import logging
from pathlib import Path

from .http.server import Server
from .storage.database import Database

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description='坡径通行编译台')
    parser.add_argument('--db', type=Path, default=Path('var/slopeway.sqlite3'))
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    database = Database(args.db)
    database.initialize()
    with Server(('127.0.0.1', args.port), database, ROOT / 'web') as server:
        print(f'http://127.0.0.1:{server.server_port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    main()
