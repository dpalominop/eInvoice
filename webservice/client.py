# -*- coding: utf-8 -*-

from pysimplesoap.client import SoapClient, SoapFault

from conf import SUNAT_WS


class Client(object):

    def __init__(self, username, password, debug=False):
        self._username = username
        self._password = password
        self._debug = debug
        self._connect()

    def _connect(self):
        self._client = SoapClient(wsdl=SUNAT_WS, cache=None, ns='ser', soap_ns='soapenv', trace=self._debug)
        self._client['wsse:Security'] = {
            'wsse:UsernameToken': {
                'wsse:Username': self._username,
                'wsse:Password': self._password
            }
        }

    def _call_service(self, name, params):
        try:
            service = getattr(self._client, name)
            return service(**params)
        except SoapFault as ex:
            print(ex)
            return None

    def send_bill(self, filename, content_file):
        params = {
            'fileName': filename,
            'contentFile': content_file
        }
        return self._call_service('sendBill', params)
