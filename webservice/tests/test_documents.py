# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

from voluptuous import MultipleInvalid

from ..models import Invoice


class InvoiceTestCase(unittest.TestCase):

    def test_valid_data(self):
        data = {
            'issue_date': datetime.today().strftime('%Y-%m-%d'),
            'supplier': {
                'ruc': '12345678909',
                'registration_name': 'Supplier',
                'commercial_name': 'commercial name',
                'address': {
                    'ubigeo': '111111',
                    'street': 'Av something',
                    'district': 'LIMA',
                    'city': 'LIMA',
                    'country_code': 'PE'
                }
            },
            'customer': {
                'ruc': '12345678909',
                'registration_name': 'Customer'
            },
            'voucher_type': '01',
            'serial': 'F001',
            'correlative': '123',
            'currency': 'PEN',
            'lines': [
                {
                    'description': 'super awesome product',
                    'price': 20.50,
                    'unit_code': 'CS'
                }
            ]
        }
        doc = Invoice('20222222223', data, None)
        doc.validate()

    def test_raise_error_with_missing_supplier_data(self):
        ruc = '20222222223'
        doc = Invoice(ruc, {
            'serial': '123',
            'correlative': '123',
            'voucher_type': '01'
        }, None)
        with self.assertRaises(MultipleInvalid):
            doc.validate()

    def test_document_name_generation(self):
        ruc = '20222222223'
        doc = Invoice(ruc, {
            'serial': 'F123',
            'correlative': '123',
            'voucher_type': '01'
        }, None)
        self.assertEqual(doc._document_name, '20222222223-01-F123-123')


if __name__ == '__main__':
    unittest.main()
