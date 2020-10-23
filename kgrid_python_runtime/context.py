class Context:
    endpoints = {}

    def get_executor_by_id(self, uri):
        hash_key = self.hash_uri(uri)
        endpoint = self.endpoints[hash_key]
        return endpoint['function']

    def get_executor_by_hash(self, hash):
        endpoint = self.endpoints[hash]
        return endpoint['function']

    def get_metadata_by_id(self, uri):
        return self.endpoints[self.hash_uri(uri)]

    def hash_uri(self, uri):
        return uri.replace('/', '_').replace('.', '_').replace('-', '_')
