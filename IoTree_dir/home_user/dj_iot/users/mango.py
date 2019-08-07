
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

import pymongo
import re
import json
import time

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)


class MongoCon:
    def __init__(self, user):
        self.user = str(user)
        self.gateway_id = ""
        self.tree_branch = []
        self.ordering = True
        self.inverting = False
        self.time_interval_min = 0.0
        self.time_interval_max = 0.0
        self.outcome = "tree"
        self.timeunix = False
        self.mongoclient = pymongo.MongoClient(config['MANGO_ADRESS'])
        self.db = self.mongoclient[config['MANGO_DATABASE']]
        # some words for time, so it can be found in the data only lowercase is nasesery
        self.times = ['zeit', 'time', 'unix']

    # meth.'s for setting values and testing if they are correct types.
    def tree(self, lists):
        if self._input_valid_(lists, 'list'):
            self.tree_branch = lists
            return True
        else:
            return False

    def start_time(self, floats):
        if self._input_valid_(floats, 'float'):
            self.time_interval_min = floats
            return True
        else:
            return False

    def end_time(self, floats):
        if self._input_valid_(floats, 'float'):
            self.time_interval_max = floats
            return True
        else:
            return False

    def order(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.ordering = boolean
            return True
        else:
            return False

    def invert(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.inverting = boolean
            return True
        else:
            return False

    def result_def(self, string):
        if self._input_valid_(string, 'str'):
            self.outcome = string
            return True
        else:
            return False

    def time_unix(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.timeunix = boolean
            return True
        else:
            return False

    def set_gateway_id(self, string):
        if self._input_valid_(string, 'str'):
            self.gateway_id = string
            return True
        else:
            return False

    # meth. for checking if given input is valid
    def _input_valid_(self, anytype, types):
        if types == 'str':
            if isinstance(anytype, str):
                a = re.match('^[a-z0-9]*$', anytype)
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

    # meth. for finding gateways for the given username
    def find_gateways(self):
        collection = self.db[config['MANGO_DATA_COL']]
        a = list(collection.find({"owner": self.user}, {"_id": 0, "gateways_id": 1}))
        if a:
            prechoices = []
            for c in a:
                prechoices.append(c['gateways_id'])
            prechoices = list(dict.fromkeys(prechoices))
            choices = []
            for b in prechoices:
                choices.append((b, b))
            return choices
        else:
            return False

    # define what will be the outcome of the query because not all stored data is needed.
    def _query_outcome_(self):
        if self.outcome == 'tree':
            queryoutcome = {"tree": 1, "_id": 0}
        elif self.outcome == 'data':
            queryoutcome = {"data": 1, "tree": 1, "_id": 0}
        else:
            return NameError
        return queryoutcome

    # make a query with the given information and settings
    def _query_find_(self):
        queryfind = {"owner": self.user, "gateways_id": self.gateway_id}
        if self.tree_branch:
            if self.ordering:
                if self.inverting:
                    i = 0
                    for n in self.tree_branch:
                        queryfind["tree."+str(i)] = {"$ne": n}
                        i += 1
                else:
                    i = 0
                    for n in self.tree_branch:
                        queryfind["tree."+str(i)] = n
                        i += 1
            else:
                if self.inverting:
                    queryfind["tree"] = {"$nin": self.tree_branch}
                else:
                    queryfind['tree'] = {"$all": self.tree_branch}
        return queryfind

    # meth. for: order the data, make it more usable for django, filter timestamps
    def _post_qurey_(self, data):
        if self.outcome == 'data':
            context = []
            for z in data:
                # collecting branch
                posts_tree = z['tree']
                # collecting data
                preposts = []
                for post in z['data']:
                    preposts.append(post)
                # get data head(fields) / headings for table and csv from data
                posts_head = []
                a = 0
                i = 0
                posts = []
                # getting longest row in data (to be sure not to miss some data)
                for n in preposts:
                    if n is not None:
                        posts.append(n)
                        b = len(n)
                        if b >= a:
                            a = b
                            longest = i
                        i += 1
                # get actual heading
                for n in posts[longest]:
                    posts_head.append(n)
                    # for .csv append also time in raw unix
                    if self.timeunix:
                        if any(word in n.lower() for word in self.times):
                            posts_head.append("U.N.I.X")
                # get actual data in to posts_body
                posts_body = []
                i = 0
                index = []
                bool_time = False
                unix_flag = False
                # values form data to array for table or csv
                for n in posts:
                    row = []
                    for m in posts_head:
                        # converting unix to readable utc if possible
                        if any(word in m.lower() for word in self.times):
                            # row.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(n.setdefault(m, ""))))
                            row.append(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(n.setdefault(m, 0))))
                            # for .csv also append raw unix time
                            if self.timeunix:
                                row.append(n.setdefault(m, ""))
                                unix_flag = True
                            if self.time_interval_max > self.time_interval_min:
                                unix_data = n.setdefault(m, 0)
                                if unix_data <= self.time_interval_min:
                                    bool_time = True
                                elif unix_data >= self.time_interval_max:
                                    bool_time = True
                        else:
                            if not unix_flag:
                                row.append(n.setdefault(m, ""))
                            else:
                                unix_flag = False
                    posts_body.append(row)
                    if bool_time:
                        index.append(i)
                        bool_time = False
                    i += 1
                for n in sorted(index, reverse=True):
                    del posts_body[n]
                # save all to a dict
                context.append({
                    'posts_body': posts_body,
                    'posts_head': posts_head,
                    'posts_tree': posts_tree
                })
            return context
        elif self.outcome == 'tree':
            context = []
            for z in data:
                posts_tree = z['tree']
                context.append(
                    {'posts_tree': posts_tree,
                     'posts_gateway_id': self.gateway_id,
                     'posts_head': '',
                     'posts_body': ''}
                )
            return context
        else:
            return data

    # meth. for finding an processing the desired data
    def find(self, shema=False):
        try:
            collection = self.db[config['MANGO_DATA_COL']]
            data = list(collection.find(self._query_find_(), self._query_outcome_()))
            if shema:
                record = self._post_qurey_(data)
            else:
                record = self._post_qurey_(data)
            self.mongoclient.close()
            return record
        except FileExistsError:
            record = []
            return record

    # meth. for fusionchart so that the data is displayed properly
    def shema(self, posts_head):
        schema = []
        for n in posts_head:
            if any(word in n.lower() for word in self.times):
                schema.append({
                    "name": n,
                    "type": "date",
                    "format": "%Y-%m-%d %H:%M:%S"
                    })
            else:
                schema.append({
                    "name": n,
                    "type": "number"
                    })
        return schema

    # meth. for deleting all data related to specific users
    def delete_all(self):
        try:
            collection = self.db[config['MANGO_DATA_COL']]
            data = collection.delete_many({"owner": self.user})
            return data
        except FileExistsError:
            return False
