from opcua import Client

from server import URI


class OPCClient:
    client = Client(URI)
    client.connect()
    client.load_type_definitions()
    root = client.get_root_node()

    @classmethod
    def get_object(cls, object_name: str):
        base_idx = cls.client.get_namespace_index(cls.client.get_namespace_array()[2])
        _object = cls.root.get_child(["0:Objects", f"{base_idx}:{object_name}"])
        _object_namespace = _object.get_browse_name()
        node = _object.get_child(f"{_object_namespace.NamespaceIndex}:{_object_namespace.Name}_vars")

        return OPCObject(name=_object_namespace.Name,
                         idx=_object_namespace.NamespaceIndex,
                         vars=node.get_value(),
                         node=node
                         )


class OPCObject:
    def __init__(self, name, idx, vars, node):
        self.name = name
        self.idx = idx
        self.vars = vars
        self.node = node

    def set_values(self, values: list[0, 1]):
        self.node.set_value(values)
        self.vars = self.node.get_value()


crane_0 = OPCClient.get_object("crane_0")
