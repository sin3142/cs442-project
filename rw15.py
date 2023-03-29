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
        """Set up the global parameters.

        Args:
            group (str): The pairing group to use.

        Returns:
            dict: The generated global parameters.
        """
        G = PairingGroup(group)
        g1 = G.random(G1)
        g2 = G.random(G2)
        egg = pair(g1, g2)
        GP = {'G': G, 'g1': g1, 'g2': g2, 'egg': egg}
        return GP

    @staticmethod
    def auth_setup(GP: dict, aid: str):
        """Set up an attribute authority.

        Args:
            GP (dict): Global parameters.
            aid (str): Unique identifier for the authority. e.g. `SingHealth`.

        Returns:
            dict, dict: The public and secret key of the authority.
        """

        G, egg, g1 = itemgetter('G', 'egg', 'g1')(GP)
        a, y = G.random(ZR), G.random(ZR)
        pk = {'aid': aid, 'egga': egg ** a, 'gy': g1 ** y}
        sk = {'aid': aid, 'a': a, 'y': y}
        return pk, sk

    @staticmethod
    def create_attr(aid: str, attr: str, value: str = None):
        """Create an attribute in the form of `attr@aid=value`.

        Args:
            aid (str): Authority identifier.
            attr (str): Attribute label.
            value (str, optional): Attribute value. Defaults to None.

        Returns:
            str: Attribute in the form of `attr@aid=value`.
        """
        return "%s@%s=%s" % (attr, aid, value) if value else "%s@%s" % (attr, aid)

    @staticmethod
    def parse_attr(attr: str):
        """Parse an attribute in the form of `attr@aid=value`.

        Args:
            attr (str): Attribute to parse. e.g. `age@SingHealth=21`.

        Returns:
            str, str, str: Attribute label, authority identifier, and value.
        """
        match = re.match(r"([\w\d]*)@([\w\d]*)(?:=([\w\d]*))?", attr)
        assert match, "Invalid attribute format"
        return match.groups()

    @staticmethod
    def keygen(GP: dict, ask: dict, gid: str, attr: str):
        """Generate a user secret key for the attribute.

        Args:
            GP (dict): Global parameters.
            ask (dict): Authority secret key.
            gid (str): User identifier.
            attr (str): Attribute in the form of `attr@aid=value`.

        Returns:
            dict: User secret key for the attribute.
        """

        aid, a, y = itemgetter('aid', 'a', 'y')(ask)
        _, auth_id, _ = RW15.parse_attr(attr)
        assert aid == auth_id, "Attribute not issued by authority"

        G, g1, g2 = itemgetter('G', 'g1', 'g2')(GP)
        H = F = lambda x: G.hash(x, G2)

        # Generate key
        t = G.random(ZR)
        K = g2 ** a * H(gid) ** y * F(attr) ** t
        Kp = g1 ** t
        return {'K': K, 'Kp': Kp}

    @staticmethod
    def auth_genkeys(GP: dict, ask: dict, gid: str, attrs: list):
        """Generate multiple user secret keys for a given authority.

        Args:
            GP (dict): Global parameters.
            ask (dict): Authority secret key.
            gid (str): User identifier.
            attrs (list): Attributes to generate keys for.

        Yields:
            str, dict: Attribute and user secret key for the attribute.
        """
        for attr in attrs:
            yield attr, RW15.keygen(GP, ask, gid, attr)

    @staticmethod
    def multiauth_genkeys(GP: dict, asks: dict, gid: str, attrs: list):
        """Generate multiple user secret keys for multiple authorities.

        Args:
            GP (dict): Global parameters.
            auths (dict): Authority secret keys. { aid: sk }
            gid (str): User identifier.
            attrs (list): Attributes to generate keys for.

        Yields:
            str, dict: Attribute and user secret key for the attribute.
        """

        for attr in attrs:
            _, aid, _ = RW15.parse_attr(attr)
            ask = asks[aid]
            yield attr, RW15.keygen(GP, ask, gid, attr)

    @staticmethod
    def encrypt(GP: dict, policy_str: str, apks: dict, msg):
        """Encrypt a message.

        Args:
            GP (dict): Global parameters.
            policy_str (str): Encryption policy, in the form of `('A' or 'B') and C`.
            apks (dict): Public keys of the authorities. { aid: pk }
            msg (G): Message to encrypt.

        Returns:
            dict: Ciphertext.
        """

        policy_tree = policy.generate_tree(policy_str)
        attributes = policy.get_attributes(policy_tree)
        assert all((RW15.parse_attr(attr)[1] in apks)
                   for attr in attributes), "Missing public key(s)"

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
            _, aid, _ = RW15.parse_attr(attr)
            tx = G.random()
            C1[attr] = egg ** secrets[attr] * \
                apks[aid]['egga'] ** tx
            C2[attr] = g1 ** -tx
            C3[attr] = apks[aid]['gy'] ** tx * g1 ** zeros[attr]
            C4[attr] = F(attr) ** tx
        return {'C0': C0, 'C1': C1, 'C2': C2, 'C3': C3, 'C4': C4, 'policy': policy_str}

    @staticmethod
    def decrypt(GP: dict, gid: str, user_sks: dict, ct: dict):
        """Decrypt a ciphertext.

        Args:
            GP (dict): Global parameters.
            gid (str): User identifier.
            user_sks (dict): User secret keys. { attr: sk }
            ct (dict): Ciphertext.

        Returns:
            G: Decrypted message.
        """

        policy_str = ct['policy']
        policy_tree = policy.generate_tree(policy_str)
        _, pruned = policy.prune_tree(policy_tree, user_sks.keys())
        if not pruned:
            raise Exception("Mising secret key(s)")

        G = itemgetter('G')(GP)
        def H(x): return G.hash(x, G2)
        coefs = {}
        policy.compute_coefs(G, policy_tree, 1, coefs)
        B = G.init(GT, 1)
        C0, C1, C2, C3, C4 = itemgetter('C0', 'C1', 'C2', 'C3', 'C4')(ct)
        for attr in policy.get_attributes(pruned):
            K, Kp = itemgetter('K', 'Kp')(user_sks[attr])
            B *= (C1[attr] * pair(C2[attr], K) * pair(C3[attr],
                  H(gid)) * pair(C4[attr], Kp)) ** coefs[attr]
        return C0 / B

    @staticmethod
    def encrypt_bytes(GP: dict, policy_str: str, apks: dict, msg: bytes):
        """Encrypt bytes.

        Args:
            GP (dict): Global parameters.
            policy_str (str): Encryption policy, in the form of `('A' or 'B') and 'C'`.
            apks (dict): Public keys of the authorities. { aid: pk }
            msg (bytes): Message to encrypt.

        Returns:
            dict: Ciphertext.
        """
        G = GP['G']
        k = G.random(GT)
        cipher = AuthenticatedCryptoAbstraction(sha2(k))
        C0 = cipher.encrypt(msg)
        C1 = RW15.encrypt(GP, policy_str, apks, k)
        return {'C0': C0, 'C1': C1}

    @staticmethod
    def decrypt_bytes(GP: dict, gid: str, user_sks: dict, ct: dict):
        """Decrypt bytes.

        Args:
            GP (dict): Global parameters.
            gid (str): User identifier.
            user_sks (dict): User secret keys. { attr: sk }
            ct (dict): Ciphertext.

        Returns:
            bytes: Decrypted message.
        """

        C0, C1 = itemgetter('C0', 'C1')(ct)
        k = RW15.decrypt(GP, gid, user_sks, C1)
        cipher = AuthenticatedCryptoAbstraction(sha2(k))
        return cipher.decrypt(C0)


def main():
    GP = RW15.global_setup('SS512')
    pk, sk = RW15.auth_setup(GP, 'A1')
    msg = GP['G'].random(GT)
    ct = RW15.encrypt(GP, "'STUDENT@A1=1'", {'A1': pk}, msg)
    k = RW15.keygen(GP, sk, 'alice', 'STUDENT@A1=1')
    pt = RW15.decrypt(GP, 'alice', {'STUDENT@A1=1': k}, ct)
    print(pt)
    print(msg)


if __name__ == "__main__":
    main()
