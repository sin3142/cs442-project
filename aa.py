#!/usr/bin/env python

import argparse
import json
import sys
from charm.toolbox.pairinggroup import PairingGroup

from rw15 import RW15
from serialize import serialize, deserialize, deserialize_gp


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Multi-Authority Attribute-based Encryption CLI')
    subparsers = parser.add_subparsers(dest='domain', required=True)

    # global-setup
    global_setup_parser = subparsers.add_parser('global-setup')
    global_setup_parser.add_argument('-g', dest='group', choices=RW15.groups, default='BN254')  # noqa
    global_setup_parser.add_argument('-o', dest='outfile', default='gp')

    #######################
    # Attribute Authority #
    #######################
    auth_parser = subparsers.add_parser('auth')
    auth_subparsers = auth_parser.add_subparsers(dest='command', required=True)

    # auth setup
    auth_setup_parser = auth_subparsers.add_parser('setup')
    auth_setup_parser.add_argument('-G', dest='gp_file', default='gp')
    auth_setup_parser.add_argument('aid')
    auth_setup_parser.add_argument('users_file')
    auth_setup_parser.add_argument('-o', dest='outfile')
    auth_setup_parser.add_argument('-opk', dest='outpubkey')

    # auth keygen
    auth_keygen_parser = auth_subparsers.add_parser('keygen')
    auth_keygen_parser.add_argument('auth_file')
    auth_keygen_parser.add_argument('gid')
    auth_keygen_parser.add_argument('password')
    auth_keygen_parser.add_argument('attrs', nargs='+')
    auth_keygen_parser.add_argument('-o', dest='outfile')

    return parser.parse_args()


def process_arguments(args):

    if args.domain == 'global-setup':

        gp = RW15.global_setup(args.group)
        with open(args.outfile, 'w') as f:
            json.dump(serialize(gp), f, indent=2)

    elif args.domain == 'auth':

        if args.command == 'setup':

            with open(args.gp_file, 'r') as f:
                gp_json = json.load(f)
                gp, G = deserialize_gp(gp_json)

            with open(args.users_file, 'r') as f:
                users = json.load(f)

            pk, sk = RW15.auth_setup(gp, args.aid)
            auth = {'gp': gp, 'pk': pk, 'sk': sk, 'users': users}

            auth_file = args.outfile or f'{args.aid}.auth'
            with open(auth_file, 'w') as f:
                json.dump(serialize(auth), f, indent=2)

            pubkey_file = args.outpubkey or f'{args.aid}.pk'
            with open(pubkey_file, 'w') as f:
                json.dump(serialize(pk), f, indent=2)

        elif args.command == 'keygen':

            with open(args.auth_file, 'r') as f:
                auth_json = json.load(f)
                gp, G = deserialize_gp(auth_json['gp'])
                auth = deserialize(auth_json, G)

            if (args.password == auth['users'][args.gid]['password']):
                if (set(args.attrs).issubset(auth['users'][args.gid]['attributes'])):
                    keys = RW15.auth_genkeys(
                        gp, auth['sk'], args.gid, args.attrs)

                    keys_file = args.outfile or f'{args.gid}.{auth["sk"]["aid"]}.keys'
                    with open(keys_file, 'w') as f:
                        json.dump(serialize(keys), f, indent=2)

                else:
                    print(args.gid + "does not have the attributes:" +
                          set(args.attrs).difference(auth['users'][args.gid]['attributes']))

            else:
                print("Wrong password")


def main():
    args = parse_arguments()
    process_arguments(args)


if __name__ == '__main__':
    main()
