# -*- coding: utf-8 -*-
# """
#     hash_ring
#     ~~~~~~~~~~~~~~
#     Implements consistent hashing that can be used when
#     the number of server nodes can increase or decrease (like in memcached).
#
#     Consistent hashing is a scheme that provides a hash table functionality
#     in a way that the adding or removing of one slot
#     does not significantly change the mapping of keys to slots.
#
#     More information about consistent hashing can be read in these articles:
#
#         "Web Caching with Consistent Hashing":
#             http://www8.org/w8-papers/2a-webserver/caching/paper2.html
#
#         "Consistent hashing and random trees:
#         Distributed caching protocols for relieving hot spots on the World Wide Web (1997)":
#             http://citeseerx.ist.psu.edu/legacymapper?did=38148
#
#
#     Example of usage::
#
#         memcache_servers = ['192.168.0.246:11212',
#                             '192.168.0.247:11212',
#                             '192.168.0.249:11212']
#
#         ring = HashRing(memcache_servers)
#         server = ring.get_node('my_key')
#

'''
有了一致性hash，你可以最小程度的减轻因为增加或者是减少服务器带来的大量的缓存MISS
在Memcached、Key-Value Store、Bittorrent DHT、LVS中都采用了Consistent Hashing算法，
可以说Consistent Hashing 是分布式系统负载均衡的首选算法
'''

import sys

if sys.version_info >= (2, 5):
    import hashlib
    md5_constructor = hashlib.md5
else:
    import md5
    md5_constructor = md5.new
class HashRing(object):
    def __init__(self, nodes=None, replicas=3):
        """Manages a hash ring.
        `nodes` is a list of objects that have a proper __str__ representation.
        `replicas` indicates how many virtual points should be used pr. node,
        replicas are required to improve the distribution.
        """
        self.replicas = replicas
        self.ring = dict()
        self._sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)
    def add_node(self, node):
        """Adds a `node` to the hash ring (including a number of replicas).
        """
        for i in range(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            self.ring[key] = node
            self._sorted_keys.append(key)
        self._sorted_keys.sort()
    def remove_node(self, node):
        """Removes `node` from the hash ring and its replicas.
        """
        for i in range(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            del self.ring[key]
            self._sorted_keys.remove(key)
    def get_node(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned.
        If the hash ring is empty, `None` is returned.
        """
        return self.get_node_pos(string_key)[0]
    def get_node_pos(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned
        along with it's position in the ring.
        If the hash ring is empty, (`None`, `None`) is returned.
        """
        if not self.ring:
            return None, None
        key = self.gen_key(string_key)
        nodes = self._sorted_keys
        for i in range(0, len(nodes)):
            node = nodes[i]
            if key  <= node:
                return self.ring[node], i
        return self.ring[nodes[0]], 0
    def get_nodes(self, string_key):
        """Given a string key it returns the nodes as a generator that can hold the key.
        The generator is never ending and iterates through the ring
        starting at the correct position.
        """
        if not self.ring:
            yield None, None
        node, pos = self.get_node_pos(string_key)
        for key in self._sorted_keys[pos:]:
            yield self.ring[key]
        while True:
            for key in self._sorted_keys:
                yield self.ring[key]
    def gen_key(self, key):
        """Given a string key it returns a long value,
        this long value represents a place on the hash ring.
        md5 is currently used because it mixes well.
        """
        m = md5_constructor()
        m.update(key.encode('utf8'))
        return m.hexdigest()

'''
下面是源代码
'''

#
# import math
# import sys
# from bisect import bisect
#
# if sys.version_info >= (2, 5):
#     import hashlib
#     md5_constructor = hashlib.md5
# else:
#     import md5
#     md5_constructor = md5.new
#
# class HashRing(object):
#
#     def __init__(self, nodes=None, weights=None):
#         """`nodes` is a list of objects that have a proper __str__ representation.
#         `weights` is dictionary that sets weights to the nodes.  The default
#         weight is that all nodes are equal.
#         """
#         self.ring = dict()
#         self._sorted_keys = []
#
#         self.nodes = nodes
#
#         if not weights:
#             weights = {}
#         self.weights = weights
#
#         self._generate_circle()
#
#     def _generate_circle(self):
#         """Generates the circle.
#         """
#         total_weight = 0
#         for node in self.nodes:
#             total_weight += self.weights.get(node, 1)
#
#         for node in self.nodes:
#             weight = 1
#
#             if node in self.weights:
#                 weight = self.weights.get(node)
#
#             factor = math.floor((40*len(self.nodes)*weight) / total_weight);
#
#             for j in range(0, int(factor)):
#                 b_key = self._hash_digest( '%s-%s' % (node, j) )
#
#                 for i in range(0, 3):
#                     key = self._hash_val(b_key, lambda x: x+i*4)
#                     self.ring[key] = node
#                     self._sorted_keys.append(key)
#
#         self._sorted_keys.sort()
#
#     def get_node(self, string_key):
#         """Given a string key a corresponding node in the hash ring is returned.
#
#         If the hash ring is empty, `None` is returned.
#         """
#         pos = self.get_node_pos(string_key)
#         if pos is None:
#             return None
#         return self.ring[ self._sorted_keys[pos] ]
#
#     def get_node_pos(self, string_key):
#         """Given a string key a corresponding node in the hash ring is returned
#         along with it's position in the ring.
#
#         If the hash ring is empty, (`None`, `None`) is returned.
#         """
#         if not self.ring:
#             return None
#
#         key = self.gen_key(string_key)
#
#         nodes = self._sorted_keys
#         pos = bisect(nodes, key)
#
#         if pos == len(nodes):
#             return 0
#         else:
#             return pos
#
#     def iterate_nodes(self, string_key, distinct=True):
#         """Given a string key it returns the nodes as a generator that can hold the key.
#
#         The generator iterates one time through the ring
#         starting at the correct position.
#
#         if `distinct` is set, then the nodes returned will be unique,
#         i.e. no virtual copies will be returned.
#         """
#         if not self.ring:
#             yield None, None
#
#         returned_values = set()
#         def distinct_filter(value):
#             if str(value) not in returned_values:
#                 returned_values.add(str(value))
#                 return value
#
#         pos = self.get_node_pos(string_key)
#         for key in self._sorted_keys[pos:]:
#             val = distinct_filter(self.ring[key])
#             if val:
#                 yield val
#
#         for i, key in enumerate(self._sorted_keys):
#             if i < pos:
#                 val = distinct_filter(self.ring[key])
#                 if val:
#                     yield val
#
#     def gen_key(self, key):
#         """Given a string key it returns a long value,
#         this long value represents a place on the hash ring.
#
#         md5 is currently used because it mixes well.
#         """
#         b_key = self._hash_digest(key)
#         return self._hash_val(b_key, lambda x: x)
#
#     def _hash_val(self, b_key, entry_fn):
#         return (( b_key[entry_fn(3)] << 24)
#                 |(b_key[entry_fn(2)] << 16)
#                 |(b_key[entry_fn(1)] << 8)
#                 | b_key[entry_fn(0)] )
#
#     def _hash_digest(self, key):
#         m = md5_constructor()
#         m.update(key.encode('utf8'))
#         return map(ord, m.digest())

#     :copyright: 2008 by Amir Salihefendic.
#     :license: BSD
# """