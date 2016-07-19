class StatusedResource(object):
    def __init__(self, id, status):
        self.id = id
        self.status = status

class CPU(StatusedResource):
    #  id', 'cores', 'speed', 'ht_enabled', 'model', 'status', 'turbo_enabled', 'vt_enabled'])
    def __init__(self, id, status):
        self.id = id
        self.status = status
        
class Memory(StatusedResource):
    #  ['id', 'size', 'speed', 'manufacturer', 'model', 'status'])
    def __init__(self, id, status):
        self.id = id
        self.status = status

class PSU(StatusedResource):
    def __init__(self, id, status):
        self.id = id
        self.status = status
