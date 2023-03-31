from rw15 import RW15

class AttributeAuthority:
    def __init__(self, aid: str, GP: dict, users: dict):
        self.id = aid
        self.GP = GP
        self.pk, self.sk = RW15.auth_setup(self.GP, self.id)
        self.users = users

    def get_encryption_key(self):
        return self.pk


    def get_decryption_key(self, gid: str, t: str, attr: str):
        if self.users.get("gid") == gid and self.users.get("token") == t:
            sk = RW15.keygen(self.GP, self.sk, gid, attr)
            return sk
        return None


    def get_decryption_keys(self, gid: str, t: str, attrs):
        if self.users.get("gid") == gid and self.users.get("token") == t:
            sk = RW15.auth_genkeys(self.GP, self.sk, gid, attrs)
            return sk
        return None


def main():
    GP = RW15.global_setup('SS512')
    Alice = {
        "gid": "81f5f01c-71ed-4f15-982b-f3da523e0272",
        "name": "Alice",
        "token": "asdfghjkjhgfd",
        "attributes": ["A"]
    }
    Bob = {
        "gid": "81f5f01c-71ed-4f15-982b-f3da523e0271",
        "name": "Bob",
        "token": "wertyuiokjhgfd",
        "attributes": ["B"]
    }

    users = {**Alice, **Bob} # only maps to Bob ????
    AA1 = AttributeAuthority('AA1', GP, users)
    AA2 = AttributeAuthority('AA2', GP, users)
    AA1pk = AA1.get_encryption_key()
    userkeyA = AA1.get_decryption_key('81f5f01c-71ed-4f15-982b-f3da523e0272', Alice.get("token"), 'A@AA1=1')
    userkeyB = AA1.get_decryption_key('81f5f01c-71ed-4f15-982b-f3da523e0271', Bob.get("token"), 'A@AA1=1')
    print(userkeyA)
    print(userkeyB)

if __name__ == "__main__":
    main()
