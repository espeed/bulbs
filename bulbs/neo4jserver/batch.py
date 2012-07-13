from .client import Neo4jRequest, Neo4jClient

#
# Batch isn't fully baked yet
#

class Neo4jBatchRequest(Neo4jRequest):
    """Makes HTTP requests to Neo4j Server and returns a Neo4jResponse.""" 
    
    def _initialize(self):
        self.messages = []
        self.message_id = 0

    def request(self, method, path, params):
        """
        Adds request to the messages list and returns a placeholder.

        :param method: HTTP method: GET, PUT, POST, or DELETE.
        :type method: str

        :param path: Path to the server resource, relative to the root URI.
        :type path: str

        :param params: Optional URI parameters for the resource.
        :type params: dict

        :rtype: str

        """
                
        return self.add_message(method, path, params)

        # return self 
        # would allow you to do self.request.post(path, params).send()
        # that won't work unless you always want to go throught the batch interface


    def add_message(self, method, path, params):
        message_id = self.next_id()
        message = dict(method=method, to=path, body=params, id=message_id)
        self.messages.append(message)
        return self.placeholder(message_id)

    def next_id(self):
        self.message_id = self.message_id + 1
        return self.message_id

    def placeholder(self, message_id):
        return "{%d}" % message_id

    def send(self):
        """
        Convenience method that sends request messages to the client.

        :param message: Tuple containing: (HTTP method, path, params)
        :type path: tuple

        :param params: Optional URI params for the resource.
        :type params: dict

        :rtype: Response

        """
        path = "batch"
        params = self.messages
        return Neo4jRequest.post(self, path, params)

    def get_messages(self):
        return self.messages

    def clear(self):
        self._initialize()


class Neo4jBatchClient(Neo4jClient):

    request_class = Neo4jBatchRequest

    # Batch isn't fully baked yet

    # Batch try (old -- from Neo4jClient)...
    #def create_indexed_vertex(self,data,index_name,keys=None):
    #    """Creates a vertex, indexes it, and returns the Response."""
    #    batch = Neo4jBatch(self.client)
    #    placeholder = batch.add(self.message.create_vertex(data))
    #    for key in keys:
    #        value = data.get(key)
    #        if value is None: continue
    #        batch.add(self.message.put_vertex(index_name,key,value,placeholder))
    #    resp = batch.send()
    #    #for result in resp.results:


    def send(self):
        return self.request.send()

    def get_messages(self):
        return self.request.get_messages()

    def clear(self):
        self.request.clear()


