#!/usr/bin/env python3
import os
import hashlib
import binascii
import unittest
import requests


class Testmeerkatfs(unittest.TestCase):
    def get_key(self):
        return b"http://iandzindo:3000/swag-" + binascii.hexlify(os.urandom(10))      #random val

    def test_getputdelete(self):
        key = self.get_key()
        print("Key: %s" % key)

        r = requests.put(key, data="liverpool", 'Failed on PUT')
        self.assertEqual(r.status_code, 201)

        r = requests.get(key)
        self.assertEqual(r.status_code, 200, 'Failed on GET')
        self.assertEqual(r.text, "liverpool", 'Failed on GET')

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200, "Failed on DELETE")


    def test_deleteworks(self):
        key = self.get_key()

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201, 'Failed on PUT')

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200, "Failed on double DELETE")

        r = requests.delete(key)
        self.assertNotEqual(r.status_code, 200, "Failed on double DELETE")


    def test_doubledelete(self):
        key = self.get_key()

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201, "Failed on PUT")

        r = requests.delete(key)
        self.assertEqual(r.status_code, 200, "Failed on DELETE")

        r = requests.get(key)
        self.assertNotEqual(r.status_code, 200, "Failed on GET")


    def test_doubleput(self):
        key = self.get_key()

        r = requests.put(key, data="liverpool")
        self.assertEqual(r.status_code, 201, 'Failed on PUT')

        r = requests.put(key, data="liverpool")
        self.assertNotEqual(r.status_code, 201, 'Failed on PUT')


    def test_10keys(self):
        keys = [self.get_key() for i in range(10)]

        for k in keys:
            r = requests.put(k, data=hashlib.md5(k).hexdigest())
            self.assertEqual(r.status_code, 201)

        for k in keys:
            r = requests.get(k)
            self.assertEqual(r.status_code, 200, "Failed on GET")
            self.assertEqual(r.text, hashlib.md5(k).hexdigest(), "Failed on GET")

        for k in keys:
            r = requests.delete(k)
            self.assertEqual(r.status_code, 200, "Faield on DELETE")

if __name__ == '__main__':
    unittest.main()
