import unittest

import app


class MyTestCase(unittest.TestCase):

    def test_upper(self):
        self.assertEqual(len(app.fileTree("Ensayos")), 12)


if __name__ == '__main__':
    unittest.main()
