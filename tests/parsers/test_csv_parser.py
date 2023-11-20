import unittest

from parsers.csv_parser import parse


class TestcsvParser(unittest.TestCase):
    def test_empty_companies_fixture(self):
        result = parse("tests/fixtures/companies_empty.csv")
        self.assertEqual(list(result), [])

    def test_sample_01_company_fixture(self):
        result = parse(filepath="tests/fixtures/companies_01.csv")
        self.assertEqual(
            set(result),
            set(["Uber", "Nike", "aws", "Home Depo"]),
        )

    def test_sample_02_company_fixture(self):
        result = parse(filepath="tests/fixtures/companies_02.csv")
        self.assertEqual(
            set(result),
            set(
                [
                    "uber",
                ]
            ),
        )

    def test_inexistent_file_should_raise_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError) as context:
            next(parse(filepath="tests/fixtures/inexistent_file_path.csv"))
