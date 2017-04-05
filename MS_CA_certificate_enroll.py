# -*- coding: utf-8 -*-
import requests
from BeautifulSoup import BeautifulSoup as Soup


def certs_enroll(ca_ip, request_file, certificates_storage, proxy=None):
    with open(request_file) as req_file:
        request_data = req_file.read()
    data = {'Mode': 'newreq',
            'CertRequest': request_data,
            'CertAttrib': 'UserAgent:Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'ThumbPrint': '',
            'TargetStoreFlags': '0',
            'SaveCert': 'yes'}
    certificate_file = open('{}/certnew.cer'.format(certificates_storage), 'w')
    certpage = requests.post('http://{}/certsrv/certfnsh.asp'.format(ca_ip), data=data, proxies=proxy)
    if certpage.status_code != 200:
        print "Can't enroll certificate"
        return
    soup = Soup(certpage.content)
    certificate_url = soup.findAll('a')[1]['href']
    request = requests.get('http://{}/certsrv/'.format(ca_ip) + certificate_url)
    if request.status_code == 200:
        certificate = requests.get('http://{}/certsrv/'.format(ca_ip) + certificate_url).content
        certificate_file.write(certificate)
        certificate_file.close()
    else:
        print "Bad certificate url"
