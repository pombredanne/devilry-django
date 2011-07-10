from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json

from ..restful import RestfulSimplifiedNode
from ...core import models, testhelper



class TestAdministratorRestfulSimplifiedNodeNoFixture(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestfulSimplifiedNode._searchform_to_kwargs({})
        self.assertEquals(kw, {'orderby': ['short_name'],
                               'start': 0,
                               'limit': 50,
                               'result_fieldgroups': None,
                               'query': u'',
                               'search_fieldgroups': None})


class TestAdministratorRestfulSimplifiedNode(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni:admin(admin1)',
                 subjects=['inf101', 'inf110'],
                 periods=['firstSem', 'secondSem:admin(admin2)'],
                 assignments=['a1', 'a2'])
        self.client = Client()
        self.client.login(username="admin1", password="test")

    def test_search(self):
        url = RestfulSimplifiedNode.get_rest_url()
        r = self.client.get(url, data={'getdata_in_qrystring': True},
                            Accept='application/json')
        self.assertEquals(r.status_code, 200)
        data = json.loads(r.content)
        first = data[0]
        self.assertEquals(first, {
            u'id': self.uni.id,
            u'short_name': self.uni.short_name,
            u'long_name': self.uni.long_name,
            u'parentnode': None
            })

    def test_create(self):
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 0)
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(short_name='testnode', long_name='Test SimplifiedNode', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 200)
        response = json.loads(r.content)
        self.assertEquals(models.Node.objects.filter(short_name='testnode').count(), 1)
        fromdb = models.Node.objects.get(id=response['id'])
        self.assertEquals(fromdb.short_name, 'testnode')
        self.assertEquals(fromdb.long_name, 'Test SimplifiedNode')
        self.assertEquals(fromdb.parentnode, None)

    def test_create_errors(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.post(url, data=json.dumps(data),
                content_type='application/json')
        self.assertEquals(r.status_code, 400)
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))

    def test_update(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(id=2, short_name='univ', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, {'id': self.uni.id,
                                     'short_name': 'univ',
                                     'long_name': 'Univ',
                                     'parentnode': None})

    def test_update_errors(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        data = dict(id=2, short_name='uniV', long_name='Univ', parentnode=None)
        r = self.client.put(url, data=json.dumps(data),
                content_type='application/json')
        response = json.loads(r.content)
        self.assertEquals(response, dict(
            fielderrors = {u'short_name': [u"Can only contain numbers, lowercase letters, '_' and '-'. "]},
            errormessages = []))


    def test_delete(self):
        url = RestfulSimplifiedNode.get_rest_url(self.uni.id)
        self.assertEquals(models.Node.objects.filter(id=self.uni.id).count(), 1)
        r = self.client.delete(url, content_type='application/json')
        self.assertEquals(models.Node.objects.filter(id=self.uni.id).count(), 0)
