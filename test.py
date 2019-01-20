from hashring import HashRing
json_dict = {
    '1':"{'NAME':'MYSQL','HOST':'192.16.1.21','USER':'ROOT','PASSWORD':'123456','PORT':3306}",
    '2':"{'NAME':'MYSQL','HOST':'192.16.1.22','USER':'ROOT','PASSWORD':'123456','PORT':3306}",
    '3':"{'NAME':'MYSQL','HOST':'192.16.1.23','USER':'ROOT','PASSWORD':'123456','PORT':3306}",
    '4':"{'NAME':'MYSQL','HOST':'192.16.1.24','USER':'ROOT','PASSWORD':'123456','PORT':3306}",
    '5':"{'NAME':'MYSQL','HOST':'192.16.1.25','USER':'ROOT','PASSWORD':'123456','PORT':3306}",

             }
memcache_servers = ['1',
                    '2',
                    '3',
                    '4',
                    '5']
weights = {
    '1':json_dict['1'],
    '2':json_dict['2'],
    '3':json_dict['3'],
    '4':json_dict['4'],
    '5':json_dict['5'],

}
ring = HashRing(memcache_servers)
server = ring.get_node('123456789')
print(server)
print(weights[server])
print(type(server))