"""
//Iotree42 sensor Network

//purpose: connecting django to pymongo to mongodb, also for checking data and process data for later use
//used software: python3, python module pymongo, json, time, re
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

import re
import json
import time
from datetime import datetime
from collections import defaultdict
import requests

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)

class FluxDataCon:
    def __init__(self, user):
        self.user = str(user)
        self.tag = "tag"
        self.tree_branch = []
        self.last = False
        self.csv = False
        self.time_interval_min = 0.0
        self.time_interval_max = 0.0
        self.fluxurl = 'http://'+str(config["FLUX_ADRESS"])+':'+str(config["FLUX_PORT"])+"/query"
        self.params = (
            ('p', config["FLUX_DJANGO_PW"]),
            ('u', config["FLUX_DJANGO_USER"]),
            ('db', self.user))
        # some words for time, so it can be found in the data only lowercase is nasesery
        self.times = ['time']

    def tree(self, lists):
        if self._input_valid_(lists, 'list'):
            self.tree_branch = lists

    def last(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.last = boolean
            return self.last

    def csv(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.csv = boolean
            return self.csv

    def start_time(self, floats):
        if self._input_valid_(floats, 'int'):
            self.time_interval_min = floats
            return self.time_interval_min

    def end_time(self, floats):
        if self._input_valid_(floats, 'int'):
            self.time_interval_max = floats
            return self.time_interval_max

    def _input_valid_(self, anytype, types):
        if types == 'str':
            if isinstance(anytype, str):
                a = re.match('^[a-z0-9A-Z/-_,]*$', anytype)
                if a:
                    return True
                else:
                    return False
        elif types == 'list':
            if isinstance(anytype, list):
                for n in anytype:
                    if isinstance(n, str):
                        a = re.match('^[a-z0-9A-Z-]*$', n)
                        if a:
                            return True
                        else:
                            return False
                    else:
                        return False
            else:
                return False
        elif types == 'boolean':
            if isinstance(anytype, bool):
                return True
            else:
                return False
        elif types == 'int':
            if isinstance(anytype, int):
                return True
            else:
                return False
        elif types == 'float':
            if isinstance(anytype, float):
                return True
            else:
                return False
        else:
            return False

    def _get_leafs_(self):
        tulpe = ('q', 'show tag values with key = "{}"'.format(self.tag))
        params = self.params + (tulpe,)
        response = requests.get(self.fluxurl, params=params)
        r = json.loads(response.text)
        leaflist  = []
        try:
            for n in r["results"][0]["series"]:
                for m in  n["values"]:
                    leaflist.append(m[1])
            return leaflist
        except:
            return leaflist

    def _get_tags_(self):
        tulpe = ('q', 'show tag values with key = "{}"'.format(self.tag))
        params = self.params + (tulpe,)
        response = requests.get(self.fluxurl, params=params)
        r = json.loads(response.text)
        taglist  = []
        try:
            for n in r["results"][0]["series"]:
                for m in  n["values"]:
                    taglist.append([i for i in m[1].split("/") if i])
            return taglist
        except:
            return taglist

    def _ctree_(self):
        return defaultdict(self._ctree_)

    def _build_leaf_(self, name, leaf, namein):

        if not namein==name:
            namein = namein+"/"+name
        res = {"text": name, "id": namein}
        # add children node if the leaf actually has any children
        if len(leaf.keys()) > 0:
            res["children"] = [self._build_leaf_(k, v, namein) for k, v in leaf.items()]
        return res

    def _make_tag_tree_(self, taglist):
        tree = self._ctree_()
        for rid, row in enumerate(taglist):
            # usage of python magic to construct dynamic tree structure and
            # basically grouping csv values under their parents
            leaf = tree[row[0]]
            for cid in range(1, len(row)):
                leaf = leaf[row[cid]]
        # building a custom tree structure
        res = []
        for name, leaf in tree.items():
            res.append(self._build_leaf_(name, leaf, name))
        return json.dumps(res)

    def get_tag_tree(self):
        content = self._make_tag_tree_(self._get_tags_())
        return content

    def _get_tags_raw_(self, giventags):
        tulpe = ('q', 'show tag values with key = "{}"'.format(self.tag))
        params = self.params + (tulpe,)
        response = requests.get(self.fluxurl, params=params)
        r = json.loads(response.text)
        giventagslist = giventags.split(",")
        taglistraw  = []
        try:
            for n in r["results"][0]["series"]:
                for m in n["values"]:
                    stri = m[1]
                    if stri.startswith(tuple(giventagslist)):
                        taglistraw.append(m[1])
            return taglistraw
        except:
            taglistraw = False
            return taglistraw

    def _query_find_(self, tags):
        data = []
        for n in tags:
            try:
                query = 'select *::field from '
                query += '"{}" '.format(n)
                query += 'where time >= {}ms and time <= {}ms'.format(self.time_interval_min, self.time_interval_max)
                tulpe = ('q', query)
                params = self.params + (tulpe,)
                response = requests.get(self.fluxurl, params=params)
                if response.text:
                    queryfind = json.loads(response.text)
                    data.append(queryfind["results"][0]["series"][0])
                del response
            except:
                print ("can not finde any entry")
        return data

    def _query_to_csv_(self, tags):
        data = []
        # open topic needs to be done
        return data

    def _query_find_last_(self, tags):
        data = []
        for n in tags:
            try:
                query = 'select *::field from '
                query += '"{}" '.format(n)
                query += 'GROUP BY * ORDER BY time DESC LIMIT 1'
                tulpe = ('q', query)
                params = self.params + (tulpe,)
                response = requests.get(self.fluxurl, params=params)
                if response.text:
                    queryfind = json.loads(response.text)
                    data.append(queryfind["results"][0]["series"][0])
            except:
                print ("can not finde any entry")
        return data

    def _post_query_(self, data):
            context = []
            if data:
                for z in data:
                    posts_tree = z['name']
                    posts_head = z['columns']
                    posts_body = z['values']
                    # save all to a dict
                    context.append({
                        'posts_body': posts_body,
                        'posts_head': posts_head,
                        'posts_tree': posts_tree
                    })
            return context

    def find(self, giventags):
        record = []
        if giventags == "":
            return record
        if self._input_valid_(giventags, 'str'):
            tags = self._get_tags_raw_(giventags)
            if tags:
                if self.last:
                    record = self._post_query_(self._query_find_last_(tags))
                elif self.csv:
                    record = self._query_to_csv_(tags)
                else:
                    record = self._post_query_(self._query_find_(tags))
                return record
            else:
                return record
        else:
            return record

    def get_raw_tags(self, giventags):
        tags = self._get_tags_raw_(giventags)
        return tags

    def get_leafs(self):
        leafs= self._get_leafs_()
        return leafs
