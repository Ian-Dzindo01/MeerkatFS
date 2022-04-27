#!/usr/bin/env python3
import os
import hashlib
import binascii
import unittest
import requests


class Testminikeyval(unittest.TestCase):
    def get_key(self):
        key = b"http://iandzindo:3000/swag-" + binascii.hexlify(os.urandom(10))      #random val


    def test_getputdelete(self):
        key = self.get_key()
        print("Key: %s" % key)

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201)

        r = requests.get(key)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "liverpool")

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200)


    def test_deleteworks(self):
        key = self.get_key()

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201)

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200)

        r = requests.delete(key)
        self.assertNotEqual(r.status_code, 200)


    def test_doubledelete(self):
        key = self.get_key()

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201)

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200)

        r = requests.get(key)
        self.assertNotEqual(r.status_code, 200)


    def test_doubleput(self):
        key = self.get_key()

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201)

        r = requests.put(key, data="liverpool")
        self.assertNotEqual(r.status_code, 201)


    def test_100keys(self):
        keys = [self.get_key() for i in range(100)]

        for k in keys:
            r = requests.put(k, data=hashlib.md5(k).hexdigest())
            self.assertEqual(r.status_code, 201)

        for k in keys:
            r = requests.get(k)
            self.assertEqual(r.text, hashlib.md5(k).hexdigest())


if __name__ == '__main__':
    unittest.main()