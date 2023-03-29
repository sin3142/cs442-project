import argparse
import json
import sys
from charm.toolbox.pairinggroup import PairingGroup, G1, G2
from charm.core.math.pairing import serialize as _serialize, deserialize as _deserialize, pc_element
from rw15 import RW15


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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Multi-Authority Attribute-based Encryption CLI')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Setup
    setup_parser = subparsers.add_parser('setup')
    setup_subparsers = setup_parser.add_subparsers(
        dest='target', required=True)

    # Setup global parameters
    setup_global_parser = setup_subparsers.add_parser('global')
    setup_global_parser.add_argument(
        '-o', '--outfile', dest='outfile', type=argparse.FileType('w'), default=sys.stdout)
    setup_global_parser.add_argument(
        'group', choices=RW15.groups, nargs='?', default='SS512')

    # Setup attribute authority
    setup_auth_parser = setup_subparsers.add_parser('auth')
    setup_auth_parser.add_argument('gp_file', type=argparse.FileType('r'))
    setup_auth_parser.add_argument('aid', type=str)

    # Setup user
    setup_user_parser = setup_subparsers.add_parser('user')
    setup_user_parser.add_argument('uid', type=str)

    # Keygen
    keygen_parser = subparsers.add_parser('keygen')
    keygen_parser.add_argument('gp_file', type=argparse.FileType('r'))
    keygen_parser.add_argument('sk_file', type=argparse.FileType('r'))
    keygen_parser.add_argument('user_file', type=argparse.FileType('r+'))
    keygen_parser.add_argument('attrs', type=str, nargs='+')

    # Encrypt
    encrypt_parser = subparsers.add_parser('encrypt')
    encrypt_parser.add_argument('gp_file', type=argparse.FileType('r'))
    encrypt_parser.add_argument('pk_files', type=argparse.FileType('r'), nargs='+')
    encrypt_parser.add_argument('policy', type=str)
    encrypt_parser.add_argument('pt_file', type=argparse.FileType('rb'))

    # Decrypt
    decrypt_parser = subparsers.add_parser('decrypt')
    decrypt_parser.add_argument('gp_file', type=argparse.FileType('r'))
    decrypt_parser.add_argument('user_file', type=argparse.FileType('r'))
    decrypt_parser.add_argument('ct_file', type=argparse.FileType('r'))

    return parser.parse_args()


def process_arguments(args):
    if args.command == 'setup':
        if args.target == 'global':
            GP = RW15.global_setup(args.group)
            json.dump(serialize(GP), args.outfile, indent=2)
            args.outfile.write('\n')
            args.outfile.close()
        elif args.target == 'auth':
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
        elif args.target == 'user':
            outfile_user = open(f'{args.uid}.user.json', 'w')
            json.dump({
                'uid': args.uid,
                'keys': {}
            }, outfile_user, indent=2)
            outfile_user.write('\n')
            outfile_user.close()
    if args.command == 'keygen':
        gp_json = json.load(args.gp_file)
        args.gp_file.close()
        sk_json = json.load(args.sk_file)
        args.sk_file.close()
        G = PairingGroup(gp_json['G']['value'])
        GP = deserialize(gp_json, G)
        SK = deserialize(sk_json, G)
        user = deserialize(json.load(args.user_file), G)
        new_uks = {attr: sk for attr, sk in RW15.auth_genkeys(
            GP, SK, user['uid'], args.attrs)}
        user['keys'].update(new_uks)
        args.user_file.seek(0)
        json.dump(serialize(user), args.user_file, indent=2)
        args.user_file.write('\n')
        args.user_file.close()
    


def main():
    args = parse_arguments()
    process_arguments(args)


if __name__ == '__main__':
    main()
