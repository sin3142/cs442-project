from charm.toolbox.pairinggroup import PairingGroup, GT, G1, G2, ZR, pair
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha2

from operator import itemgetter
import policy
import re


class RW15:

    groups = ['SS512', 'SS1024', 'MNT159', 'MNT201', 'MNT224', 'BN254']

    @staticmethod
    def global_setup(group: str):
        G = PairingGroup(group)
        g1 = G.random(G1)
        g2 = G.random(G2)
        egg = pair(g1, g2)
        GP = {'G': G, 'g1': g1, 'g2': g2, 'egg': egg}
        return GP

    @staticmethod
    def auth_setup(GP: dict, aid: str):
        G, egg, g1 = itemgetter('G', 'egg', 'g1')(GP)
        a, y = G.random(ZR), G.random(ZR)
        pk = {'aid': aid, 'egga': egg ** a, 'gy': g1 ** y}
        sk = {'aid': aid, 'a': a, 'y': y}
        return pk, sk

    @staticmethod
    def create_attr(aid: str, attr: str, value: str = None):
        return "%s@%s=%s" % (attr, aid, value) if value else "%s@%s" % (attr, aid)

    @staticmethod
    def parse_attr(attr: str):
        match = re.match(r"([\w\d]*)@([\w\d]*)(?:=([\w\d]*))?", attr)
        assert match, "Invalid attribute format"
        return match.groups()

    @staticmethod
    def keygen(GP: dict, sk: dict, gid: str, attr: str):
        G, g1, g2 = itemgetter('G', 'g1', 'g2')(GP)
        H = F = lambda x: G.hash(x, G2)
        aid, a, y = itemgetter('aid', 'a', 'y')(sk)

        assert aid == RW15.parse_attr(attr)[1], f"Attribute {attr} does not belong to authority {aid}"  # noqa

        t = G.random(ZR)
        K = g2 ** a * H(gid) ** y * F(attr) ** t
        Kp = g1 ** t
        return {'K': K, 'Kp': Kp}

    @staticmethod
    def auth_genkeys(GP: dict, sk: dict, gid: str, attrs: list):
        keys = {}
        for attr in attrs:
            keys[attr] = RW15.keygen(GP, sk, gid, attr)
        return keys

    @staticmethod
    def encrypt(GP: dict, policy_str: str, pk_dict: dict, msg):

        policy_tree = policy.generate_tree(policy_str)
        attributes = policy.get_attributes(policy_tree)

        required_auths = set()
        for attr in attributes:
            required_auths.add(RW15.parse_attr(attr)[1])

        missing_auths = required_auths - set(pk_dict.keys())
        if missing_auths:
            raise Exception(f"Missing public key(s): {missing_auths}")

        G, g1, egg = itemgetter('G', 'g1', 'egg')(GP)
        def F(x): return G.hash(x, G2)
        z = G.random(ZR)
        w = G.init(ZR, 0)

        secrets, zeros = {}, {}
        policy.generate_shares(G, policy_tree, z, secrets)
        policy.generate_shares(G, policy_tree, w, zeros)

        # Generate ciphertext
        C0 = msg * (egg ** z)
        C1, C2, C3, C4 = {}, {}, {}, {}
        for attr in attributes:
            aid = RW15.parse_attr(attr)[1]
            tx = G.random()
            C1[attr] = egg ** secrets[attr] * \
                pk_dict[aid]['egga'] ** tx
            C2[attr] = g1 ** -tx
            C3[attr] = pk_dict[aid]['gy'] ** tx * g1 ** zeros[attr]
            C4[attr] = F(attr) ** tx
        return {'C0': C0, 'C1': C1, 'C2': C2, 'C3': C3, 'C4': C4, 'policy': policy_str}

    @staticmethod
    def decrypt(GP: dict, gid: str, sk_dict: dict, ct: dict):
        policy_str = ct['policy']
        policy_tree = policy.generate_tree(policy_str)
        _, pruned = policy.prune_tree(policy_tree, sk_dict.keys())
        if not pruned:
            raise Exception("Missing secret key(s)")

        G = itemgetter('G')(GP)
        def H(x): return G.hash(x, G2)
        coefs = {}
        policy.compute_coefs(G, policy_tree, 1, coefs)
        B = G.init(GT, 1)
        C0, C1, C2, C3, C4 = itemgetter('C0', 'C1', 'C2', 'C3', 'C4')(ct)
        for attr in policy.get_attributes(pruned):
            K, Kp = itemgetter('K', 'Kp')(sk_dict[attr])
            B *= (C1[attr] * pair(C2[attr], K) * pair(C3[attr],
                  H(gid)) * pair(C4[attr], Kp)) ** coefs[attr]
        return C0 / B

    @staticmethod
    def encrypt_bytes(GP: dict, policy_str: str, pk_dict: dict, msg: bytes):
        G = GP['G']
        k = G.random(GT)
        cipher = AuthenticatedCryptoAbstraction(sha2(k))
        C0 = cipher.encrypt(msg)
        C1 = RW15.encrypt(GP, policy_str, pk_dict, k)
        return {'C0': C0, 'C1': C1}

    @staticmethod
    def decrypt_bytes(GP: dict, gid: str, sk_dict: dict, ct: dict):
        C0, C1 = itemgetter('C0', 'C1')(ct)
        k = RW15.decrypt(GP, gid, sk_dict, C1)
        cipher = AuthenticatedCryptoAbstraction(sha2(k))
        return cipher.decrypt(C0)


def main():
    GP = RW15.global_setup('SS512')
    pk, sk = RW15.auth_setup(GP)
    msg = GP['G'].random(GT)
    ct = RW15.encrypt(GP, "'STUDENT@A1=1'", {'A1': pk}, msg)
    k = RW15.keygen(GP, sk, 'alice', 'STUDENT@A1=1')
    pt = RW15.decrypt(GP, 'alice', {'STUDENT@A1=1': k}, ct)
    print(pt)
    print(msg)


if __name__ == "__main__":
    main()
