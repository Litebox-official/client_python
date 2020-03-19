from __future__ import unicode_literals

import sys
import time
from multiprocessing import Pool

from fakeredis import FakeStrictRedis

from prometheus_client import (
    CollectorRegistry, Counter, Gauge, Histogram, Summary
)

from prometheus_client.providers import get_redis_provider

from prometheus_client.openmetrics.exposition import generate_latest

if sys.version_info < (2, 7):
    # We need the skip decorators from unittest2 on Python 2.6.
    import unittest2 as unittest
else:
    import unittest


class TestProvider(unittest.TestCase):
    """Test cases for provider."""

    def setUp(self):
        self.registry = CollectorRegistry()

        # Mock time so _created values are fixed.
        self.old_time = time.time
        time.time = lambda: 123.456
        redis_app = FakeStrictRedis()
        self.redis_provider = get_redis_provider(redis_app)

    def tearDown(self):
        time.time = self.old_time

    def test_counter(self):
        c = Counter('cc', 'A counter', registry=self.registry,
                    storage_provider=self.redis_provider)
        c.inc()
        self.assertEqual(b'# HELP cc A counter\n# TYPE cc counter\ncc_total 1.0\ncc_created 123.456\n# EOF\n',
                         generate_latest(self.registry))

    def test_gauge(self):
        g = Gauge('gg', 'A gauge', registry=self.registry,
                  storage_provider=self.redis_provider)
        g.set(17)
        self.assertEqual(
            b'# HELP gg A gauge\n# TYPE gg gauge\ngg 17.0\n# EOF\n',
            generate_latest(self.registry))

    def test_summary(self):
        s = Summary('ss', 'A summary', ['a', 'b'], registry=self.registry,
                    storage_provider=self.redis_provider)
        s.labels('c', 'd').observe(17)
        self.assertEqual(b"""# HELP ss A summary
# TYPE ss summary
ss_count{a="c",b="d"} 1.0
ss_sum{a="c",b="d"} 17.0
ss_created{a="c",b="d"} 123.456
# EOF
""", generate_latest(self.registry))

    @unittest.skipIf(sys.version_info < (2, 7),
                     "Test requires Python 2.7+.")
    def test_histogram(self):
        s = Histogram('hh', 'A histogram', registry=self.registry,
                      storage_provider=self.redis_provider)
        s.observe(0.05)
        self.assertEqual(b"""# HELP hh A histogram
# TYPE hh histogram
hh_bucket{le="0.005"} 0.0
hh_bucket{le="0.01"} 0.0
hh_bucket{le="0.025"} 0.0
hh_bucket{le="0.05"} 1.0
hh_bucket{le="0.075"} 1.0
hh_bucket{le="0.1"} 1.0
hh_bucket{le="0.25"} 1.0
hh_bucket{le="0.5"} 1.0
hh_bucket{le="0.75"} 1.0
hh_bucket{le="1.0"} 1.0
hh_bucket{le="2.5"} 1.0
hh_bucket{le="5.0"} 1.0
hh_bucket{le="7.5"} 1.0
hh_bucket{le="10.0"} 1.0
hh_bucket{le="+Inf"} 1.0
hh_count 1.0
hh_sum 0.05
hh_created 123.456
# EOF
""", generate_latest(self.registry))
