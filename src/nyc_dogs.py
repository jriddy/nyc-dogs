import csv
import logging
import pathlib
from typing import Sequence, MutableMapping, Iterable, Mapping

import attr
from tornado import ioloop, web


logger = logging.getLogger(__name__)


def ilen(xs: Iterable) -> int:
    """
    Count number of instances in any finite-length iterable.

    :param xs: any iterable, don't pass infinite iterables here.
    :returns: number of instances

    This does not allocate any temporary memory just to get length.
    Note: this consumes generators.  Copy to list if you need that.

    Todo: I feel like this exists in the stdlib or a common library
    somewhere, i just can't remember...
    """
    acc = 0
    for _ in xs:
        acc += 1
    return acc


@attr.s
class DataCounter:
    """
    Class for perfoming the count operations on the data.

    :attribute _records: list of mappings of dog data
    """
    _records: Sequence[MutableMapping[str, str]] = attr.ib(repr=False)
    _column_names: Sequence[str] = attr.ib()

    @_column_names.default
    def _read_column_names(self):
        return list(self._records[0].keys())

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
        """
        Return the column names as a sequence.
        """
        return self._column_names

    def occurances(self, values: Mapping[str, str]) -> int:
        """
        Count occurances of the ``value`` in ``column, case-insentively.

        :param column: column name
        :param value: value to compare with
        :returns: count of instances in record data
        """
        keys, vals = zip(*((k.lower(), v.lower()) for k, v in values.items()))
        series = (tuple(rec[k].lower() for k in keys) for rec in self._records)
        return ilen(tup for tup in series if tup == vals)


class CountHandler(web.RequestHandler):

    def initialize(self, counter):
        self.counter = counter

    def get(self) -> None:
        """
        Do a count query.

        Writes its JSON responses to the client, sending a 400 code on bad args.
        """
        raw_args = self.request.arguments
        args = {k.lower(): v[-1].decode('utf-8') for k, v in raw_args.items()}
        logging.debug("got count args: %s", args)
        unknown = set(args).difference(self.counter.columns)
        if unknown:
            self.write({"unknown fields": sorted(unknown)})
            self.set_status(400)
            return
        self.write({"count": self.counter.occurances(args)})
        # Tornado appends charset thing, which the test doesn't like
        self.set_header('Content-Type', 'application/json')


def make_application(data_path) -> web.Application:
    counter = DataCounter.load_csv(data_path)
    return web.Application([
        (r'/count', CountHandler, {'counter': counter}),
    ])


def main(default_port=5000):
    import sys
    # TODO: better arg parsing
    port = int(sys.argv[1])
    logging.basicConfig(level=logging.INFO)
    default_csv = pathlib.Path(__file__).parent / 'data/dogs-nyc.csv'
    app = make_application(pathlib.Path(default_csv))
    app.listen(port)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
