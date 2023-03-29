from rw15 import RW15
from attributeauthority import AttributeAuthority

# WIP
# generate and integrate auth token

def get_keys(aid: str, u: dict, gid: str, attrs: list):
    # get decryption keys from AA
    GP = RW15.global_setup('SS512')
    AA = AttributeAuthority(aid, GP, u)

    k = AA.get_decryption_keys(gid, attrs) 
    return k

def get_doc():
    # get ciphertext from database (WIP, DO NOT RUN)
    ct = 0
    return ct

def decrypt(gid: str, k: dict, ct: dict):
    # decrypt ciphertext (WIP, DO NOT RUN)
    GP = RW15.global_setup('SS512')
    pt = RW15.decrypt(GP, gid, k, ct)
    return pt

def main(): 
    print("DEMO USE CASE 1")

    # setup users
    Doctor = {"D1234567@GovAA": { 
        "attributes": ["SingHealth@GovAA","NHCS@SingHealthAA", "Doctor@SingHealthAA", "Cardiology@SingHealthAA", "Diagnosis@SingHealthAA", "Detailed@GovA", "Summary@GovAA"]
    }}

    Nurse = {"N6767676@GovAA": { 
        "attributes": ["SingHealth@GovAA","NHCS@SingHealthAA", "Doctor@SingHealthAA", "Diagnosis@SingHealthAA", "Detailed@GovA", "Summary@GovAA"]
    }}
  
    users = {**Doctor, **Nurse}
    
    # get keys from AA
    dk = get_keys("GovAA", users, "D1234567@GovAA", Doctor.get("D1234567@GovAA").get("attributes"))
    nk = get_keys("GovAA", users, "N6767676@GovAA", Nurse.get("N6767676@GovAA").get("attributes"))

    # get ciphertext from database (WIP, DO NOT RUN)
    ct = get_doc()

    # decrypt ciphertext (WIP, DO NOT RUN)
    dpt = decrypt("D1234567@GovAA", dk, ct)
    npt = decrypt("N6767676@GovAA", nk, ct)

    print("TEST END")

if __name__ == "__main__":
    main()