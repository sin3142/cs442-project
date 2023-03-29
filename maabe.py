import argparse
import json
from charm.toolbox.pairinggroup import PairingGroup, G1, G2
from charm.core.math.pairing import serialize as _serialize, deserialize as _deserialize, pc_element
from rw15 import RW15


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Multi-Authority Attribute-based Encryption CLI')

    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # Setup
    setup_parser = subparsers.add_parser('setup')
    setup_subparsers = setup_parser.add_subparsers(
        dest='command', required=True)

    # Setup global parameters
    setup_global_parser = setup_subparsers.add_parser('global')
    setup_global_parser.add_argument(
        '-o', '--outfile', dest='outfile', type=argparse.FileType('w'), default='gp.json')
    setup_global_parser.add_argument(
        'group', choices=RW15.groups, nargs='?', default='SS512')

    # Setup attribute authority
    setup_aa_parser = setup_subparsers.add_parser('aa')
    setup_aa_parser.add_argument(
        '-G', dest='gp_file', type=argparse.FileType('r'), default='gp.json')
    setup_aa_parser.add_argument('aid')

    return parser.parse_args()


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


def process_arguments(args):
    if args.subcommand == 'setup':
        if args.command == 'global':
            GP = RW15.global_setup(args.group)
            print(GP)
            json.dump(serialize(GP), args.outfile, indent=2)
            args.outfile.write('\n')
            args.outfile.close()
        elif args.command == 'aa':
            gp_json = json.load(args.gp_file)
            args.gp_file.close()
            G = PairingGroup(gp_json['G']['value'])
            GP = deserialize(gp_json, G)
            pk, sk = RW15.auth_setup(GP, args.aid)
            outfile_pk = open(f'{args.aid}.pk.json', 'w')
            json.dump(serialize(pk), outfile_pk, indent=2)
            outfile_pk.write('\n')
            outfile_pk.close()
            outfile_sk = open(f'{args.aid}.sk.json', 'w')
            json.dump(serialize(sk), outfile_sk, indent=2)
            outfile_sk.write('\n')
            outfile_sk.close()


def main():
    args = parse_arguments()
    process_arguments(args)


if __name__ == '__main__':
    main()
