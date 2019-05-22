import pymongo
import re


class MongoCon:
    def __init__(self, gateway_id, user):
        self.user = user
        self.gateway_id = gateway_id
        self.tree_branch = []
        self.ordering = True
        self.inverting = False
        self.timeintervall = ""
        self.outcome = "tree"
        self.mongoclient = pymongo.MongoClient('mongodb://xxxxxxxxxxxx:xxxxx/')
        self.db = self.mongoclient.SensorData

    def tree(self, lists):
        if self._input_valid_(lists, 'list'):
            self.tree_branch = lists

    def order(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.ordering = boolean

    def invert(self, boolean):
        if self._input_valid_(boolean, 'boolean'):
            self.inverting = boolean

    def resultdef(self, string):
        if self._input_valid_(string, 'str'):
            self.outcome = string

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
        else:
            return False

    def _user_valid_(self):
        collection = self.db.xxxxx
        a = collection.find({"username": self.user, "serialnum": self.gateway_id}, {"_id": 1})
        if list(a):
            return True
        else:
            return False

    def _query_outcome_(self):  # define what will be the outcome of the query because not all stored data is needed
        if self.outcome == 'tree':
            queryoutcome = {"tree": 1, "_id": 0}
        elif self.outcome == 'data':
            queryoutcome = {"data": 1, "tree": 1, "_id": 0}
        else:
            return NameError
        return queryoutcome

    def _query_find_(self):
        queryfind = {"gateways_id": self.gateway_id}
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

    def _post_qurey_(self, data):
        if self.outcome == 'data':
            context = []
            for z in data:
                posts_tree = z['tree']
                posts = []
                for post in z['data']:
                    posts.append(post)
                posts_head = []
                for n in posts[0]:  # headings for table and csv from data
                    posts_head.append(n)
                posts_body = []
                # converting unix to readable utc if possible
                # some words for time, so it can be found in the data only lowercase is nassery
                times = ['zeit', 'time', 'unix']
                # values form data to array for table or csv
                for n in posts:
                    row = []
                    for m in n:
                        if any(word in m.lower() for word in times):  # converting unix to readable utc if possible
                            import time
                            row.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(n[m])))
                        else:
                            row.append(n[m])
                    posts_body.append(row)
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
                     'posts_head': '',
                     'posts_body': ''}
                )
            return context
        else:
            return data

    def find(self):
        if self._input_valid_(self.gateway_id, 'str') and self._user_valid_():
            collection = self.db.xxxxxxxx
            a = list(collection.find(self._query_find_(), self._query_outcome_()))
            if a:
                record = self._post_qurey_(a)
            else:
                record = a
            self.mongoclient.close()
            return record
        else:
            record = []
            return record
