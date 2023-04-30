import timeit
import io
import sys

import pickle
from xml_marshaller import xml_marshaller
import json
from proto import data_pb2
import fastavro
import yaml
import msgpack

data = {"string": "string",
        "array" : [1, 2, 3],
        "dict": {"Defence": "Nimso", "Levi": "Roam"},
        "number": 100,
        "point_number": 1.009}


def native_format():
    ser_data = pickle.dumps(data)
    ser_data_size = sys.getsizeof(ser_data)

    serialization_time = timeit.timeit(lambda: pickle.dumps(data), number=1000)

    deserialization_time = timeit.timeit(lambda: pickle.loads(ser_data), number=1000)

    return (ser_data_size, serialization_time, deserialization_time)

def xml_format():
    ser_data = xml_marshaller.dumps(data)
    ser_data_size = sys.getsizeof(ser_data)

    serialization_time = timeit.timeit(lambda: xml_marshaller.dumps(data), number=1000)

    deserialization_time = timeit.timeit(lambda: xml_marshaller.loads(ser_data), number=1000)

    return (serialization_time, deserialization_time, ser_data_size)

def json_format():
    ser_data = json.dumps(data)
    ser_data_size = sys.getsizeof(ser_data)
    
    serialization_time = timeit.timeit(lambda: json.dumps(data), number=1000)

    deserialization_time = timeit.timeit(lambda: json.loads(ser_data), number=1000)

    return (serialization_time, deserialization_time, ser_data_size)

def protobuf_format():
    msg = data_pb2.TestingStruct()
    msg.string = data["string"]
    msg.number = data["number"]
    for value in data["array"]:
        msg.array.append(value)
    for key, value in data["dict"].items():
        msg.dict[key] = value

    ser_data = msg.SerializeToString()
    ser_data_size = sys.getsizeof(ser_data)
    
    serialization_time = timeit.timeit(lambda: msg.SerializeToString(), number=1000)

    deserialization_time = timeit.timeit(lambda: data_pb2.TestingStruct.FromString(ser_data), number=1000)

    return (serialization_time, deserialization_time, ser_data_size)

def apache_avro_format():
    schema = {
        "type": "record",
        "name": "avro.test",
        "fields": [
            {"name": "string", "type": "string"},
            {"name": "array", "type": {"type": "array", "items": "int"}},
            {"name": "dict", "type": {"type": "map", "values": "string"}},
            {"name": "number", "type": "int"},
            {"name": "point_number", "type": "float"}
        ]
    }

    bytes_writer = io.BytesIO()
    fastavro.schemaless_writer(bytes_writer, schema, data)
    ser_data = bytes_writer.getvalue()
    ser_data_size = sys.getsizeof(ser_data)
    
    serialization_time = timeit.timeit(lambda: fastavro.schemaless_writer(io.BytesIO(), schema, data), number=1000)

    deserialization_time = timeit.timeit(lambda: fastavro.schemaless_reader(io.BytesIO(ser_data), schema), number=1000)
    
    return (serialization_time, deserialization_time, ser_data_size)

def yaml_format():
    ser_data = yaml.dump(data)
    ser_data_size = sys.getsizeof(ser_data)

    serialization_time = timeit.timeit(lambda: yaml.dump(data), number=100)

    deserialization_time = timeit.timeit(lambda: yaml.load(ser_data, Loader=yaml.FullLoader), number=100)

    return (serialization_time, deserialization_time, ser_data_size)

def msg_pack_format():
    ser_data = msgpack.packb(data, use_bin_type=True)
    ser_data_size = sys.getsizeof(ser_data)

    serialization_time = timeit.timeit(lambda: msgpack.packb(data, use_bin_type=True), number=1000)

    deserialization_time = timeit.timeit(lambda: msgpack.unpackb(ser_data, raw=False), number=1000)

    return (ser_data_size, serialization_time, deserialization_time)


NAME_TO_CONVERTER = {
    'NATIVE': native_format,
    'JSON': json_format,
    'XML': xml_format,
    'GOOGLE_BUFFER': protobuf_format,
    'APACHE': apache_avro_format,
    'YAML': yaml_format,
    'MESSAGEPACK': msg_pack_format,
}
