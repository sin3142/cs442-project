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

    setup_parser = subparsers.add_parser('setup')

    setup_subparsers = setup_parser.add_subparsers(dest='type', required=True)
    setup_global_parser = setup_subparsers.add_parser('global')
    setup_auth_parser = setup_subparsers.add_parser('auth')
    setup_user_parser = setup_subparsers.add_parser('user')

    keygen_parser = subparsers.add_parser('keygen')
    add_keys_parser = subparsers.add_parser('add-keys')
    encrypt_parser = subparsers.add_parser('encrypt')
    decrypt_parser = subparsers.add_parser('decrypt')

    setup_global_parser.add_argument('-o', dest='outfile', default='gp.json')
    setup_global_parser.add_argument('-g', dest='group', choices=RW15.groups, default='BN254')  # noqa

    setup_auth_parser.add_argument('-G', dest='gp_file', default='gp.json')
    setup_auth_parser.add_argument('aid')

    setup_user_parser.add_argument('gid')

    keygen_parser.add_argument('-G', dest='gp_file', default='gp.json')
    keygen_parser.add_argument('-o', dest='outfile')
    keygen_parser.add_argument('sk_file')
    keygen_parser.add_argument('gid')
    keygen_parser.add_argument('attrs', nargs='+')

    add_keys_parser.add_argument('user_file')
    add_keys_parser.add_argument('key_files', nargs='+')

    encrypt_parser.add_argument('-G', dest='gp_file', default='gp.json')
    encrypt_parser.add_argument('-o', dest='outfile')
    encrypt_parser.add_argument('policy')
    encrypt_parser.add_argument('pt_file')
    encrypt_parser.add_argument('pk_files', nargs='+')

    decrypt_parser.add_argument('-G', dest='gp_file', default='gp.json')
    decrypt_parser.add_argument('-o', dest='outfile')
    decrypt_parser.add_argument('user_file')
    decrypt_parser.add_argument('ct_file')

    return parser.parse_args()


def process_arguments(args):
    if args.command == 'setup':

        if args.type == 'global':

            GP = RW15.global_setup(args.group)

            with open(args.outfile, 'w') as outfile:
                json.dump(serialize(GP), outfile, indent=2)
                outfile.write('\n')

        elif args.type == 'auth':

            with open(args.gp_file, 'r') as gp_file:
                gp_json = json.load(gp_file)

            G = PairingGroup(gp_json['G']['value'])
            GP = deserialize(gp_json, G)
            pk, sk = RW15.auth_setup(GP, args.aid)

            with open(f'{args.aid}.pk.json', 'w') as outfile_pk:
                json.dump(serialize(pk), outfile_pk, indent=2)
                outfile_pk.write('\n')
            with open(f'{args.aid}.sk.json', 'w') as outfile_sk:
                json.dump(serialize(sk), outfile_sk, indent=2)
                outfile_sk.write('\n')

        elif args.type == 'user':

            with open(f'{args.gid}.user.json', 'w') as outfile_user:
                json.dump({
                    'gid': args.gid,
                    'keys': {}
                }, outfile_user, indent=2)
                outfile_user.write('\n')

    if args.command == 'keygen':

        with open(args.gp_file, 'r') as gp_file:
            gp_json = json.load(gp_file)
        with open(args.sk_file, 'r') as sk_file:
            sk_json = json.load(sk_file)

        G = PairingGroup(gp_json['G']['value'])
        GP = deserialize(gp_json, G)
        SK = deserialize(sk_json, G)
        keys = {attr: sk for attr, sk in RW15.auth_genkeys(
            GP, SK, args.gid, args.attrs)}

        if not args.outfile:
            args.outfile = f'{args.gid}-{SK["aid"]}.keys.json'
        with open(args.outfile, 'w') as outfile:
            json.dump(serialize(keys), outfile, indent=2)
            outfile.write('\n')

    if args.command == 'add-keys':

        with open(args.user_file, 'r') as user_file:
            user_json = json.load(user_file)
        keys = {}
        for key_file in args.key_files:
            with open(key_file, 'r') as key_file:
                keys.update(json.load(key_file))

        user_json['keys'].update(keys)

        with open(args.user_file, 'w') as user_file:
            json.dump(user_json, user_file, indent=2)
            user_file.write('\n')

    if args.command == 'encrypt':

        with open(args.gp_file, 'r') as gp_file:
            gp_json = json.load(gp_file)
        with open(args.pt_file, 'rb') as pt_file:
            pt = pt_file.read()

        G = PairingGroup(gp_json['G']['value'])
        GP = deserialize(gp_json, G)
        pks = {}
        for pk_file in args.pk_files:
            with open(pk_file, 'r') as pk_file:
                pk_json = json.load(pk_file)
            pk = deserialize(pk_json, G)
            pks[pk['aid']] = pk
        ct = RW15.encrypt_bytes(GP, args.policy, pks, pt)

        if not args.outfile:
            args.outfile = f'{args.pt_file}.ct.json'
        with open(args.outfile, 'w') as outfile:
            json.dump(serialize(ct), outfile, indent=2)
            outfile.write('\n')

    if args.command == 'decrypt':

        with open(args.gp_file, 'r') as gp_file:
            gp_json = json.load(gp_file)
        with open(args.user_file, 'r') as user_file:
            user_json = json.load(user_file)
        with open(args.ct_file, 'r') as ct_file:
            ct_json = json.load(ct_file)

        G = PairingGroup(gp_json['G']['value'])
        GP = deserialize(gp_json, G)
        user = deserialize(user_json, G)
        ct = deserialize(ct_json, G)
        pt = RW15.decrypt_bytes(GP, user['gid'], user['keys'], ct)

        if not args.outfile:
            args.outfile = f'{args.ct_file}.pt'
        with open(args.outfile, 'wb') as outfile:
            outfile.write(pt)


def main():
    args = parse_arguments()
    process_arguments(args)


if __name__ == '__main__':
    main()
