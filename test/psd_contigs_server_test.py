import unittest
import os
import json
import time

from os import environ
from ConfigParser import ConfigParser
from pprint import pprint

from biokbase.workspace.client import Workspace as workspaceService
from psd_contigs.psd_contigsImpl import psd_contigs


class psd_contigsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.ctx = {'token': token}
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('psd_contigs'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = psd_contigs(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_psd_contigs_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_count_contigs(self):
        obj_name = "contigset.1"
        contig = {'id': '1', 'length': 10, 'md5': 'md5', 'sequence': 'agcttttcat'}
        obj = {'contigs': [contig], 'id': 'id', 'md5': 'md5', 'name': 'name', 
                'source': 'source', 'source_id': 'source_id', 'type': 'type'}
        self.getWsClient().save_objects({'workspace': self.getWsName(), 'objects':
            [{'type': 'KBaseGenomes.ContigSet', 'name': obj_name, 'data': obj}]})
        ret = self.getImpl().count_contigs(self.getContext(), self.getWsName(), obj_name)
        self.assertEqual(ret[0]['contig_count'], 1)
        