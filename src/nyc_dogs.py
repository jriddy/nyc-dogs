import csv
import logging
import pathlib
from typing import Sequence, MutableMapping

import attr
from tornado import httpclient, ioloop, web


logger = logging.getLogger(__name__)


@attr.s
class DataCounter:
    """
    Class for perfoming the count operations on the data.

    :attribute _records: list of mappings of dog data
    """
    _records: Sequence[MutableMapping[str, str]] = attr.ib(repr=False)

    @classmethod
    def load_csv(cls, filepath: pathlib.Path) -> 'DataCounter':
        """
        Create an instance of this class from CSV.
        """
        with open(filepath, 'r') as file:
            records = list(csv.DictReader(file))
            logger.info("loaded %d records", len(records))
            return cls(records)

    @property
    def columns(self) -> Sequence[str]:
        return list(self._records[0].keys())


class CountHandler(web.RequestHandler):

    def initialize(self, counter):
        self.counter = counter

    def get(self) -> None:
        self.write({"hello": self.counter.columns})


def make_application(data_path) -> web.Application:
    counter = DataCounter.load_csv(data_path)
    return web.Application([
        (r'/count', CountHandler, {'counter': counter}),
    ])


def main():
    logging.basicConfig(level=logging.INFO)
    app = make_application(pathlib.Path('data/dogs-nyc.csv'))
    app.listen(8888)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
