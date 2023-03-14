from charm.schemes.abenc.abenc_maabe_rw15 import MaabeRW15
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha2


class MaabeRW15Hybrid(MaabeRW15):

    def encrypt(self, gp, pks, message: bytes, policy_str: str):
        key = self.group.random(GT)
        c1 = super().encrypt(gp, pks, key, policy_str)
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        c2 = cipher.encrypt(message)
        return {'c1': c1, 'c2': c2}

    def decrypt(self, gp, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = super().decrypt(gp, sk, c1)
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        return cipher.decrypt(c2)


def main():
    group = PairingGroup('SS512')
    maabe = MaabeRW15Hybrid(group)
    gp = maabe.setup()
    pk, sk = maabe.authsetup(gp, "AUTH")
    pks = {"AUTH": pk}
    sks = {
        "GID": "user",
        "keys": maabe.multiple_attributes_keygen(gp, sk, "user", ['ONE@AUTH'])
    }

    access_policy = '(one@auth)'
    message = b"hello world this is an important message."
    cipher_text = maabe.encrypt(gp, pks, message, access_policy)
    print(maabe.decrypt(gp, sks, cipher_text))


if __name__ == "__main__":
    main()
