"""Test suite for SPG4."""

import os
from unittest import TestCase
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4

thisdir = os.path.dirname(__file__)


class SatRec(object):
    pass


class Tests(TestCase):

    def test_tle_verify(self):
        whichconst = 'wgs72'
        actual = generate_test_output(whichconst)

        tcppath = os.path.join(thisdir, 'tcppver.out')
        with open(tcppath) as tcpfile:
            for i, expected_line in enumerate(tcpfile):
                if i:
                    print i,
                    import sys
                    sys.stdout.flush()

                # TODO: what are we supposed to do with the extra fields
                # that lie past character 107?
                if len(expected_line) > 107:
                    expected_line = expected_line[:107] + expected_line[-1:]

                try:
                    actual_line = next(actual)
                except StopIteration:
                    print 'WARNING: our output ended early, on line %d' % (i+1)
                    break

                if actual_line != expected_line:
                    raise ValueError(
                        'Line %d of output does not match:\n'
                        '\n'
                        'Expect: %s'
                        'Actual: %s'
                        % (i + 1, expected_line, actual_line))


def generate_test_output(whichconst):
    """Generate lines like those in the test file tcppver.out."""

    tlepath = os.path.join(thisdir, 'SGP4-VER.TLE')
    with open(tlepath) as tlefile:
        tlelines = iter(tlefile.readlines())

    for line1 in tlelines:

        if not line1.startswith('1'):
            continue

        line2 = next(tlelines)

        satrec = SatRec()
        twoline2rv(line1, line2, 'c', None, 'i', whichconst, satrec)
        yield '%ld xx\n' % (satrec.satnum,)

        ro, vo = sgp4(whichconst, satrec, 0.0)
        yield format_test_line(satrec, ro, vo)

        tstart, tend, tstep = (float(field) for field in line2[69:].split())

        tsince = tstart
        while tsince <= tend:
            if tsince == 0.0:
                tsince += tstep
                continue  # avoid duplicating the first line

            ro, vo = sgp4(whichconst, satrec, tsince)
            yield format_test_line(satrec, ro, vo)

            tsince += tstep


def format_test_line(satrec, ro, vo):
    return ' %16.8f %16.8f %16.8f %16.8f %12.9f %12.9f %12.9f\n' % (
        satrec.t, ro[0], ro[1], ro[2], vo[0], vo[1], vo[2])
