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
    auth_setup_parser.add_argument('-o', dest='outfile')
    auth_setup_parser.add_argument('-opk', dest='outpubkey')

    # auth keygen
    auth_keygen_parser = auth_subparsers.add_parser('keygen')
    auth_keygen_parser.add_argument('auth_file')
    auth_keygen_parser.add_argument('gid')
    auth_keygen_parser.add_argument('attrs', nargs='+')
    auth_keygen_parser.add_argument('-o', dest='outfile')

    ########
    # User #
    ########
    user_parser = subparsers.add_parser('user')
    user_subparsers = user_parser.add_subparsers(dest='command', required=True)

    # user setup
    user_setup_parser = user_subparsers.add_parser('setup')
    user_setup_parser.add_argument('-G', dest='gp_file', default='gp')
    user_setup_parser.add_argument('gid')
    user_setup_parser.add_argument('-o', dest='outfile')

    # user add-keys
    user_add_keys_parser = user_subparsers.add_parser('add-keys')
    user_add_keys_parser.add_argument('user_file')
    user_add_keys_parser.add_argument('key_files', nargs='+')

    # user remove-keys
    user_remove_keys_parser = user_subparsers.add_parser('remove-keys')
    user_remove_keys_parser.add_argument('user_file')
    user_remove_keys_parser.add_argument('attrs', nargs='+')

    # user decrypt
    user_decrypt_parser = user_subparsers.add_parser('decrypt')
    user_decrypt_parser.add_argument('user_file')
    user_decrypt_parser.add_argument('ciphertext_file')
    user_decrypt_parser.add_argument('-o', dest='outfile')

    ##############
    # Data Owner #
    ##############

    # create-policy
    policy_setup_parser = subparsers.add_parser('create-policy')
    policy_setup_parser.add_argument('-G', dest='gp_file', default='gp')
    policy_setup_parser.add_argument('policy')
    policy_setup_parser.add_argument('pubkey_files', nargs='+')
    policy_setup_parser.add_argument('-o', dest='outfile')

    # encrypt
    encrypt_parser = subparsers.add_parser('encrypt')
    encrypt_parser.add_argument('policy_file')
    encrypt_parser.add_argument('plaintext_file')
    encrypt_parser.add_argument('-o', dest='outfile')

    return parser.parse_args()


def process_arguments(args):

    if args.domain == 'global-setup':

        gp = RW15.global_setup(args.group)
        with open(args.outfile, 'w') as f:
            json.dump(serialize(gp), f, indent=2)

    elif args.domain == 'create-policy':

        with open(args.gp_file, 'r') as f:
            gp_json = json.load(f)
            gp, G = deserialize_gp(gp_json)

        pk_dict = {}
        for pubkey_file in args.pubkey_files:
            with open(pubkey_file, 'r') as f:
                pk = deserialize(json.load(f), G)
                pk_dict[pk['aid']] = pk  # no pubkey signatures

        policy = {'gp': gp, 'policy': args.policy, 'pk_dict': pk_dict}

        # Test policy
        RW15.encrypt_bytes(policy['gp'], policy['policy'], policy['pk_dict'], b'test')  # noqa

        policy_file = args.outfile or f'{args.policy}.policy'
        with open(policy_file, 'w') as f:
            json.dump(serialize(policy), f, indent=2)

    elif args.domain == 'encrypt':

        with open(args.policy_file, 'r') as f:
            policy_json = json.load(f)
            gp, G = deserialize_gp(policy_json['gp'])
            policy = deserialize(policy_json, G)

        with open(args.plaintext_file, 'rb') as f:
            plaintext = f.read()

        gp, policy, pk_dict = policy['gp'], policy['policy'], policy['pk_dict']
        ciphertext = RW15.encrypt_bytes(gp, policy, pk_dict, plaintext)

        ciphertext_file = args.outfile or f'{args.plaintext_file}.ct'
        with open(ciphertext_file, 'w') as f:
            json.dump(serialize(ciphertext), f, indent=2)

    elif args.domain == 'auth':

        if args.command == 'setup':

            with open(args.gp_file, 'r') as f:
                gp_json = json.load(f)
                gp, G = deserialize_gp(gp_json)

            pk, sk = RW15.auth_setup(gp, args.aid)
            auth = {'gp': gp, 'pk': pk, 'sk': sk}

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

            keys = RW15.auth_genkeys(gp, auth['sk'], args.gid, args.attrs)

            keys_file = args.outfile or f'{args.gid}.{auth["sk"]["aid"]}.keys'
            with open(keys_file, 'w') as f:
                json.dump(serialize(keys), f, indent=2)

    elif args.domain == 'user':

        if args.command == 'setup':

            with open(args.gp_file, 'r') as f:
                gp_json = json.load(f)
                gp, G = deserialize_gp(gp_json)

            user = {'gp': gp, 'gid': args.gid, 'keys': {}}

            user_file = args.outfile or f'{args.gid}.user'
            with open(user_file, 'w') as f:
                json.dump(serialize(user), f, indent=2)

        elif args.command == 'add-keys':

            with open(args.user_file, 'r') as f:
                user_json = json.load(f)
                gp, G = deserialize_gp(user_json['gp'])
                user = deserialize(user_json, G)

            for key_file in args.key_files:
                with open(key_file, 'r') as f:
                    keys_json = json.load(f)
                    keys = deserialize(keys_json, G)
                    user['keys'].update(keys)

            with open(args.user_file, 'w') as f:
                json.dump(serialize(user), f, indent=2)

        elif args.command == 'remove-keys':

            with open(args.user_file, 'r') as f:
                user_json = json.load(f)
                gp, G = deserialize_gp(user_json['gp'])
                user = deserialize(user_json, G)

            for attr in args.attrs:
                del user['keys'][attr]

            with open(args.user_file, 'w') as f:
                json.dump(serialize(user), f, indent=2)

        elif args.command == 'decrypt':

            with open(args.user_file, 'r') as f:
                user_json = json.load(f)
                gp, G = deserialize_gp(user_json['gp'])
                user = deserialize(user_json, G)

            with open(args.ciphertext_file, 'r') as f:
                ciphertext_json = json.load(f)
                ciphertext = deserialize(ciphertext_json, G)

            plaintext = RW15.decrypt_bytes(gp, user['gid'], user['keys'], ciphertext)  # noqa

            plaintext_file = args.outfile or f'{args.ciphertext_file}.pt'
            with open(plaintext_file, 'wb') as f:
                f.write(plaintext)


def main():
    args = parse_arguments()
    process_arguments(args)


if __name__ == '__main__':
    main()
