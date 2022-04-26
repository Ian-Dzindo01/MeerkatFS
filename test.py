#!/usr/bin/env python3
import os
import binascii
import unittest
import requests

class Testminikeyval(unittest.TestCase):
    def test_getputdelete(self):
        key = b"http://localhost:3000/swag-" + binascii.hexlify(os.urandom(10))        # random val
        print("Key: %s" % key)

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 200)

        r = requests.get(key)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "liverpool")

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()
