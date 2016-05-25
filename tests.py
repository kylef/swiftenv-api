import unittest

from versions import Version


class VersionTests(unittest.TestCase):
    def test_version_not_snapshot(self):
        version = Version('2.2.0', {})
        self.assertFalse(version.is_snapshot)

    def test_version_is_snapshot(self):
        version = Version('2.2.1-SNAPSHOT-2016-04-23-a', {})
        self.assertTrue(version.is_snapshot)

    def test_version_supports_known_platform(self):
        version = Version('2.2.0', {'test': 'http://example.com/test.pkg'})
        self.assertTrue(version.supports_platform('test'))

    def test_version_doesnt_support_unknown_platform(self):
        version = Version('2.2.0', {})
        self.assertFalse(version.supports_platform('test'))

    def test_versions(self):
        versions = Version.objects.versions
        self.assertTrue(len(versions) > 0)
