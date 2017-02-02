import unittest

from twitter_text_analyzer import break_blocks

class TestTextAnalyzer(unittest.TestCase):
    def test_block_breaker(self):
        self.assertEqual(break_blocks('1234Python'), '1234 Python')
        self.assertEqual(break_blocks('1234PythonLanguage352SomeText'), '1234 Python Language 352 Some Text')
        self.assertEqual(break_blocks('1234PythonLanguage352SomeText2017'), '1234 Python Language 352 Some Text 2017')
        self.assertEqual(break_blocks('WOMENForTrump2017'), 'WOMEN For Trump 2017')
        self.assertEqual(break_blocks('WOMENForTrump2017AfterINAUGURATIONDay'), 'WOMEN For Trump 2017 After '
                                                                                'INAUGURATION Day')

        self.assertNotEqual(break_blocks('1234PythonLanguage3.5.2SomeText'), '1234 Python Language 3.5.2 Some Text')
        self.assertNotEqual(break_blocks('NZvsAUS'), 'NZ vs AUS')

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__ == '__main__':
    unittest.main()
