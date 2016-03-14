from keen import scoped_keys
from keen.tests.base_test_case import BaseTestCase


class ScopedKeyTests(BaseTestCase):
    api_key = "24077ACBCB198BAAA2110EDDB673282F8E34909FD823A15C55A6253A664BE368"
    bad_api_key = "24077ACBCB198BAAA2110EDDB673282F8E34909FD823A15C55A6253A664BE369"
    old_api_key = "ab428324dbdbcfe744"
    old_bad_api_key = "badbadbadbad"
    options = {
        "filters": [{
            "property_name": "accountId",
            "operator": "eq",
            "property_value": "123456"
        }]
    }

    def test_scoped_key_encrypts_and_decrypts(self):
        encrypted = scoped_keys.encrypt(self.api_key, self.options)
        decrypted = scoped_keys.decrypt(self.api_key, encrypted)
        self.assert_equal(decrypted, self.options)

    def test_scoped_key_fails_decryption_bad_key(self):
        encrypted = scoped_keys.encrypt(self.api_key, self.options)
        try:
            scoped_keys.decrypt(self.bad_api_key, encrypted)
            self.fail("shouldn't get here")
        except ValueError as e:
            self.assert_is_not_none(e)

    def test_old_scoped_key_encrypts_and_decrypts(self):
        encrypted = scoped_keys.encrypt(self.old_api_key, self.options)
        decrypted = scoped_keys.decrypt(self.old_api_key, encrypted)
        self.assert_equal(decrypted, self.options)

    def test_old_scoped_key_fails_decryption_on_bad_key(self):
        encrypted = scoped_keys.encrypt(self.old_api_key, self.options)
        try:
            scoped_keys.decrypt(self.old_bad_api_key, encrypted)
            self.fail("shouldn't get here")
        except ValueError as e:
            self.assert_is_not_none(e)
