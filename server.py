from opcua import Server
import random
import time
from device_codes import Codes


URI = "opc.tcp://0.0.0.0:4840/server/"
GENERAL_NAMESPACE = 'http://object.test'


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


class OPCServer:
    server = Server()
    server.set_endpoint(URI)
    server.set_server_name("OPC-Mock")

    handler = SubHandler()
    sub = None

    @classmethod
    def create_handler(cls, instance):
        return cls.sub.subscribe_data_change(instance)

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
        cls.sub = cls.server.create_subscription(5, cls.handler)


class OPCObject:
    def __init__(self, namespace: str, name: str, variables: list):
        self.namespace = OPCServer.register_namespace(namespace)
        self.instance = OPCServer.create_object_in_namespace(self.namespace, name)
        self.variables = self.instance.add_variable(self.namespace, f"{name}_vars", variables)
        self.variables.set_writable()   # Set node as writable by clients. A node is always writable on server side.
        OPCServer.create_handler(self.variables)

    def set_value(self, values: list):
        self.variables.set_value(values)
        OPCServer.create_handler(self.variables)

    def get_value(self):
        return self.variables.get_value()


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


def shuffle_objects(objects, iterations: int, sleep: int | float = None):

    for step in range(iterations):
        for val in objects:
            values = val.get_value()
            random.shuffle(values)
            val.set_value(values)
            # val.handler = OPCServer.create_handler(val.variables)
            if sleep:
                time.sleep(sleep)


if __name__ == '__main__':
    OPCServer.start()
    objects = generate_objects()
    shuffle_objects(objects, 5)
    print("Total objects:\n", [val.instance.get_browse_name().Name for val in objects])
