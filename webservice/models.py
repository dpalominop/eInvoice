# -*- coding: utf-8 -*-

import base64
import os
import zipfile

from jinja2 import FileSystemLoader, Environment
from lxml import etree
from signxml import xmldsig
from voluptuous import Schema, Required, All, Length, ALLOW_EXTRA, Optional
from cStringIO import StringIO


path_dir = os.path.dirname(os.path.realpath(__file__))
attach_dir = os.path.join(path_dir, 'attach')
loader = FileSystemLoader('./templates')
env = Environment(loader=loader)


class Document(object):

    template_name = ''

    def __init__(self, ruc, data, client):
        self._ruc = ruc
        self._data = data
        self._xml = None
        self._document_name = self.generate_document_name()
        self._data.update({
            'document_name': self._document_name,
            'ruc': self._ruc,
            'voucher_number': '{}-{}'.format(self._data['serial'], self._data['correlative'])
        })
        self._client = client
        self._response = None
        self._zip_path = None
        self.in_memory_data = StringIO()
        self.in_memory_zip = zipfile.ZipFile(self.in_memory_data, "w", zipfile.ZIP_DEFLATED, False)

    def generate_document_name(self):
        """
        implement document name generation
        """
        raise NotImplementedError

    def validate(self):
        """
        implement data validation
        """
        raise NotImplementedError

    def render(self):
        template = env.get_template(self.template_name)
        self._xml = template.render(**self._data)

    def sign(self):
        # TODO: change hardcodeed key paths to environement variables
        cert = open('cert.pem').read()
        key = open('key.pem').read()

        root = etree.fromstring(self._xml.encode('ISO-8859-1'), parser=etree.XMLParser(encoding='ISO-8859-1'))
        signed_root = xmldsig(root, digest_algorithm='sha1').sign(algorithm='rsa-sha1', key=key, cert=cert)
        signed_root.xpath('//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature',
                          namespaces={'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
                                      'ds': 'http://www.w3.org/2000/09/xmldsig#'})[0].attrib['Id'] = 'SignSUNAT'
        self._xml = etree.tostring(signed_root, encoding='ISO-8859-1')

        print (xmldsig(signed_root).verify(require_x509=True, x509_cert=cert,
                                           ca_pem_file=key, ca_path=None,
                                           hmac_key=None, validate_schema=True,
                                           parser=None, id_attribute=None))

    def writetofile(self, filename, filecontent):
        self.in_memory_zip.writestr(filename, filecontent)

    def prepare_zip(self):
        self._zip_filename = '{}.zip'.format(self._document_name)
        nx = '{}.xml'.format(self._document_name)
        self.writetofile(nx, self._xml)
        for zfile in self.in_memory_zip.filelist:
            zfile.create_system = 0
        self.in_memory_zip.close()

    def send(self):
        encoded_content = base64.b64encode(self.in_memory_data.getvalue())
        self._response = self._client.sendBill(self._zip_filename, encoded_content)

    def process_response(self):
        # save in disk response content
        if self._response is not None:
            response_data = self._response['applicationResponse']
            decoded_response_content = base64.b64decode(response_data)
            zip_file = open('response.zip', 'w')  # TODO: generate this filename
            zip_file.write(decoded_response_content)
            zip_file.close()

    def process(self):
        self.validate()
        self.render()
        self.sign()
        self.prepare_zip()
        self.send()
        self.process_response()
        return self._response


class Invoice(Document):

    template_name = 'invoice.xml'
    voucher_type = ''

    def validate(self):
        supplier = Schema({
            Required('ruc'): All(str, Length(min=11, max=11)),
            Required('registration_name'): str,
            Optional('address'): dict,
            Optional('commercial_name'): str
        }, extra=ALLOW_EXTRA)
        customer = Schema({
            Required('ruc'): All(str, Length(min=1, max=11))
        }, extra=ALLOW_EXTRA)
        schema = Schema({
            Required('issue_date'): str,
            Required('supplier'): supplier,
            Required('customer'): customer,
            Required('voucher_type'): str,
            Required('currency'): str,
            Required('voucher_number'): str,
            Required('lines'): All(list, Length(min=1))
        }, extra=ALLOW_EXTRA)
        schema(self._data)

    def generate_document_name(self):
        """
        Tipo de comprobante
        01: Factura electronica
        03: Boleta de venta
        07: Nota de credito
        08: Nota de debito
        Serie del comprobante
        FAAA: Facturas
        BAAA: Boletas
        """
        # TODO: Add types as constants in diferent classes
        return '{ruc}-{type}-{serial}-{correlative}'.format(
            ruc=self._ruc,
            type=self._data['voucher_type'],
            serial=self._data['serial'],
            correlative=self._data['correlative']
        )
