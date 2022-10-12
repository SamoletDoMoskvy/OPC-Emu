from opcua import Server
from device_codes import Codes

URI = "opc.tcp://0.0.0.0:4840/server/"
GENERAL_NAMESPACE = 'http://object.test'


class OPCServer:
    server = Server()
    server.set_endpoint(URI)
    server.set_server_name("OPC-Mock")

    @classmethod
    def register_namespace(cls, name: str):
        return cls.server.register_namespace(name)  # Register a new namespace. Nodes should in custom namespace, not 0.

    @classmethod
    def create_object_in_namespace(cls, namespace: int, object_name: str):
        cls.objects = cls.server.get_objects_node()  # Get Objects node of server. Returns a Node object.
        return cls.objects.add_object(namespace, object_name)

    @classmethod
    def start(cls):
        cls.server.start()


class OPCObject:
    def __init__(self, namespace: str, name: str, variables: list):
        self.namespace = OPCServer.register_namespace(namespace)
        self.instance = OPCServer.create_object_in_namespace(self.namespace, name)
        self.variables = self.instance.add_variable(self.namespace, f"{name}_vars", variables)
        self.variables.set_writable()   # Set node as writable by clients. A node is always writable on server side.

    def set_variable_value(self, values):
        self.variables.set_value(values)    # Set value of a node


def generate_objects() -> list[object]:
    _objects = []
    namespace = dict(Codes.__dict__.keys().mapping)
    del namespace['__module__'], namespace['__dict__'], namespace['__weakref__'], namespace['__doc__']

    for n, key in enumerate(namespace):
        _objects.append(
            OPCObject(
                namespace=GENERAL_NAMESPACE,
                name=key.replace('codes_', ''),
                variables=[int(val) for val in namespace[key].values()]
            )
        )

    return _objects


if __name__ == '__main__':
    objects = generate_objects()
    print([val.instance.get_browse_name().Name for val in objects])

    OPCServer.start()
