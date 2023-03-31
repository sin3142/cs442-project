from rw15 import RW15
from attributeauthority import AttributeAuthority
import secrets as sc

class User:
    def __init__(self, gid: str, t: str, attrs: list): # initialise user object
        self.gid = gid
        self.token = t
        self.attrs = attrs

    def get_keys(self, aid: str, u: dict):  # get decryption keys from AA
        GP = RW15.global_setup('SS512')
        AA = AttributeAuthority(aid, GP, u)

        # get_keys debug code
        print("test get_keys")
        print(self.gid)
        print(u.get("gid"))
        print("")

        k = AA.get_decryption_keys(self.gid, self.token, self.attrs) 
        return k

    def get_doc(): # get ciphertext from database (WIP, DO NOT RUN)
        ct = 0
        return ct

    def decrypt(gid: str, k: dict, ct: dict): # decrypt ciphertext (WIP, DO NOT RUN)
        GP = RW15.global_setup('SS512')
        pt = RW15.decrypt(GP, gid, k, ct)
        return pt

def main(): 
    print("DEMO USE CASE 1\n")

    # setup users
    dattr = ["SingHealth@GovAA","NHCS@SingHealthAA", "Doctor@SingHealthAA", "Cardiology@SingHealthAA", "Diagnosis@SingHealthAA", "Detailed@GovA", "Summary@GovAA"]
    dt = sc.token_hex(20)
    Doctor = User("D1234567@GovAA", dt, dattr)

    nattr = ["SingHealth@GovAA","NHCS@SingHealthAA", "Doctor@SingHealthAA", "Diagnosis@SingHealthAA", "Detailed@GovA", "Summary@GovAA"]
    nt = sc.token_hex(20)
    Nurse = User("N6767676@GovAA", nt, nattr)
    
    users = {**Doctor.__dict__, **Nurse.__dict__} # doesn't map doctor ???????
    
    # get keys from AA
    dk = Doctor.get_keys("GovAA", users)
    nk = Nurse.get_keys("GovAA", users)

    # get_keys debug code
    print("dk:", dk)
    print("nk:", nk)

    # get ciphertext from database (WIP, DO NOT RUN)
    # ct = get_doc()

    # decrypt ciphertext (WIP, DO NOT RUN)
    # dpt = decrypt("D1234567@GovAA", dk, ct)
    # npt = decrypt("N6767676@GovAA", nk, ct)

    print("DEMO END")

if __name__ == "__main__":
    main()