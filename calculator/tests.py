import unittest
from pkg.calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_addition(self):
        self.assertEqual(self.calculator.evaluate("3 + 5"), 8)

    def test_subtraction(self):
        self.assertEqual(self.calculator.evaluate("10 - 4"), 6)

    def test_multiplication(self):
        self.assertEqual(self.calculator.evaluate("3 * 4"), 12)

    def test_division(self):
        self.assertEqual(self.calculator.evaluate("10 / 2"), 5)

    def test_nested_expression(self):
        self.assertEqual(self.calculator.evaluate("3 * 4 + 5"), 17)

    def test_complex_expression(self):
        self.assertEqual(self.calculator.evaluate("2 * 3 - 8 / 2 + 5"), 7)

    def test_empty_expression(self):
        self.assertIsNone(self.calculator.evaluate(""))

    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            self.calculator.evaluate("$ 3 5")

    def test_not_enough_operands(self):
        with self.assertRaises(ValueError):
            self.calculator.evaluate("+ 3")

    def test_precedence(self):
        self.assertEqual(self.calculator.evaluate("3 + 7 * 2"), 17)

if __name__ == "__main__":
    unittest.main()
