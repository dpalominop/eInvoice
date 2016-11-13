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
    
    #Recibe un archivo zip con un unico documento XML de comprobante.
    #Devuelve un archivo zip con un documento XML que es la constancia de aceptacion o rechazo.
    def sendBill(self, filename, content_file):
        params = {
            'fileName': filename,
            'contentFile': content_file
        }
        return self._call_service('sendBill', params)

    #Recibe un archivo zip con un unico documento XML de resumenes
    #(resumen de boletas, comunicacion de baja, reversiones de comprobantes de percepció y recepcion).
    #Devuelve un ticket (Str) con el que usando el metodo getStatus se obtiene el archivo zip 
    #conteniendo el documento XML que es la constancia de aceptacion o rechazo.
    def sendSummary(self, filename, content_file):
        params = {
            'fileName': filename,
            'contentFile': content_file
        }
        return self._call_service('sendSummary', params)

    #Recibe un archivo zip con un unico documento XML de resumenes
    #(facturas, boletas de venta, notas de credito y debito).
    #Devuelve un ticket (Str) con el que usando el metodo getStatus se obtiene el archivo zip 
    #conteniendo varios documentos XML que es la constancia de aceptacion o rechazo por documento enviado y un archivo resumen.
    def sendPack(self, filename, content_file):
        params = {
            'fileName': filename,
            'contentFile': content_file
        }
        return self._call_service('sendPack', params)
    
    #Recibe el ticket (Str)
    #Devuelve un objeto que indica el estado del proceso y en caso de haber terminado,
    # devuelve adjunta la constancia de aceptacion o rechazo y el reporte de envio (para el caso de lotes)
    def getStatus(self, ticket):
        params = {
            'ticket': ticket
        }
        return self._call_service('getStatus', params)

    #Recibe como parametro los datos de comprobante de pago (ruc del emisor, tipo de comprobante, serie y numero de comprobante).
    #Devuelve un archivo zip que contiene el documento XML de la constancia de recepcion.
    def getStatusCdr(self, rucComprobante):
        params = {
            'rucComprobante': rucComprobante
        }
        return self._call_service('getStatusCdr', params)
