import json
from charm.toolbox.pairinggroup import PairingGroup
from charm.core.math.pairing import serialize as _serialize, deserialize as _deserialize, pc_element


def serialize(element):
    if isinstance(element, dict):
        return {k: serialize(v) for k, v in element.items()}
    if isinstance(element, pc_element):
        return {
            'type': 'pc_element',
            'value': _serialize(element, True).decode()
        }
    if isinstance(element, PairingGroup):
        return {
            'type': 'pairing_group',
            'value': element.groupType()
        }
    return element


def deserialize(element, group=None):
    if isinstance(element, dict):
        if element.get('type') == 'pc_element':
            return _deserialize(group.Pairing, element['value'].encode(), True)
        elif element.get('type') == 'pairing_group':
            return PairingGroup(element['value'])
        else:
            return {k: deserialize(v, group) for k, v in element.items()}
    else:
        return element


def deserialize_gp(gp_json):
    G = deserialize(gp_json['G'])
    return deserialize(gp_json, G), G
