#!/usr/bin/env python

import argparse
import json
import sys
from charm.toolbox.pairinggroup import PairingGroup

from rw15 import RW15
from serialize import serialize, deserialize, deserialize_gp

gp = {
    "G": {
      "type": "pairing_group",
      "value": "BN254"
    },
    "g1": {
      "type": "pc_element",
      "value": "1:F8nuDqIuvxk+uGu4Qpz7DqGAnYbC4OulXOvk8tlE3wYA"
    },
    "g2": {
      "type": "pc_element",
      "value": "2:EX/qQy7Hz362PWk9Gb0ruAu/93xEKJiKXS5hiMfg8f0F8V84EuqROAuOx/yNbEfavevWWmxRsSEBlEiZYWsUJgA="
    },
    "egg": {
      "type": "pc_element",
      "value": "3:GqCiHZfHTDtE3JyzliNndJ93vvp6WU2XWfkK462RTLYghBwXSjPKcoun0noRj6EP3exaoXU5BbLlBVo4vx6Lkx1GoA8eYeUo/XIMFnBBWpMiDSYLUmmxEaJALzmhuzLcEPSYqiuej8jwf8y1ek0gQWDIHYI+1wxJEkaGkxlqXLAYTF4XgA0cPL1kqzsagX5+Kwc2s9vL7opIx9bjwJ0aLwIskjabOcR5VedshDAwhizpu4gYIVEXPH1+LlVO0I9jIymUshOpNRDzJFOdQVhbprPinr9WviEpYCbmfG3947MdU/OZEbx7iqqYhFI/Py1wrSQkuiYt1F/kp/LdhNJYgRDvEOWv7QWfIM5cajoRrChnWbcU4rTPcZWktqhBciGvFCQzob1GmXaW+0okEaZfOLcQ9ZlPlriLAbcOUe+ArYwSxA4eZ0RRn0QXHn1u6ONWzWOql37L7k3OswI4pizvZhkzRfv9Yuq8WJ8PQm+pHn8a4HeXGjM/IIRISPOFgzqD"
    }
  }

auths = {
    "MOH": {
        "pk": {
            "aid": "MOH",
            "egga": {
            "type": "pc_element",
            "value": "3:FfYpjTVHe//zU/mgqkqKV2KCGXe2ZL08ej1m0+S8IaYDIOu+s7pXEpPX4B1FXvAXLhuzaipOgBliCeb3dY67Xw+Q1AhBw5AcB0AaWWX6ceF4OHpiS/79fUQ266laUlq1ATLM9cfWxImwLYfOPaba1zxe9U1JcOLKvC1pNWVIX3QTJvq9HGw5NKIfRljd1Rsd7MZoZBI8l+ecvtcRnyUpfgoMF1t6vLNcj5XTmpiDBwMphWxdMgv/wKDjuwkgdlmOFs/Ukt5yAOpKH5sNHZbw2ivmW1OKu4kL48u60yuhORwGvMpOMLucmKPt4sC3c0oEbMfemVqmQi1pjm8jLXxFjgeyO0+00fe+ADgUTsj7UMWsfAdJLRWs3g+Eg5yCI3ccCqZcifoNjjbQf1+UKv28ej9zApG5Nv0QPqdiKsQifd4BozPazMj8pB/etob/d+wTy8A3q4805acYDl3u2W0zvR9a9fuM38nm3PxCAnfIeGMJaChL/hMSJzZEGtJRCAao"
            },
            "gy": {
            "type": "pc_element",
            "value": "1:H9p02StJ4WFjuWOuFVHz5IYkVHjcyEjQWCoxUsTy7j8A"
            }
        },
        "sk": {
            "aid": "MOH",
            "a": {
            "type": "pc_element",
            "value": "0:Fsrc0uZGaJjGbcpx6Zrt3T85nAJZLMSM3PTagiovsG8="
            },
            "y": {
            "type": "pc_element",
            "value": "0:FK6vNnLUM+0H9jnvJ8N/zuoZtujt+C+ZsjjGDadhAVo="
            }
        },
        "users": {
            "tan": {
                "password": "natrotcod",
                "attributes": ["qual@MOH=doctor", "spt@MOH=surgery"]
            },
            "lee": {
                "password": "eelrotcod",
                "attributes": ["qual@MOH=doctor", "spt@MOH=cardiology"]
            },
            "lim": {
                "password": "milrotcod",
                "attributes": ["qual@MOH=doctor", "spt@MOH=pediatrics"]
            },
            "tay": {
                "password": "yatesrun",
                "attributes": ["qual@MOH=nurse"]
            },
            "wong": {
                "password": "gnowtsicamrahp",
                "attributes": ["qual@MOH=pharmacist"]
            }
        }
    },
    "SH": {
        "pk": {
            "aid": "SH",
            "egga": {
            "type": "pc_element",
            "value": "3:FxotdugmrHHHwQDIdkiHjJBOpK/hqZeB5Bv+/xo4yA4EnegWUgnmRr8A+rJK1DJy4RZQhaIoRXLmw/9KdKzLfhCof627hx1bR3FJ1umUo8K0eyRuCMTvpxYket2VBwSmGGgq2fSzh5+unfdmVbwfW36nypZrdmxCDIE1HHPdRgIIHPZ9aGjclN+NyEqVlmjMwCVSz8qcdg4ld77MPpkwiwR02h7ZmYNRIJ2allH110JMKnA/9W1gFj7YLle6/wD4Fz+urFwZxIE1o2AqYSZudaNhDQS4ENHM8hccXNZN3NYRZttWOrPawY1on9dc42Zm43qnG6KJn1t9y2MDYOLTnRFJz9PiSTD8GkbmDyvp6UGcUGQ3ZKYSAlYSfNO8lu7iCoAfQoNHG9WIvhmSnJ/PZZru9S1IzO33OXDeAfaDPHUjFteu822Wdqs0xbAKnuNmho2lgWkWe+iRfLTmRAU62yMB0DtRh1HrW0rI2Bb3icMYK1sxfag+JJO5RhXL6ubw"
            },
            "gy": {
            "type": "pc_element",
            "value": "1:CE/I0E2Nf34lcdYdAhyZ+EZWiuBBuldjX2/YXIGhzR4A"
            }
        },
        "sk": {
            "aid": "SH",
            "a": {
            "type": "pc_element",
            "value": "0:G9Lv6Bm3ExuXfw0gLmRXJ9RqWJRJ1w2yszQYelkW1M8="
            },
            "y": {
            "type": "pc_element",
            "value": "0:D5rhzVT+VGy/1CvKk8zxGAPPAYrKCpd8r3vx/kOv99s="
            }
        },
        "users": {
            "tan": {
                "password": "natrotcod",
                "attributes": ["clr@SH=low", "clr@SH=med"]
            },
            "lim": {
                "password": "milrotcod",
                "attributes": ["clr@SH=low", "clr@SH=med", "clr@SH=high"]
            },
            "goh": {
                "password": "hogrehcraeser",
                "attributes": ["prp@SH=research", "grp@SH=SMU"]
            },
            "chua": {
                "password": "auhctnegaecnarusni",
                "attributes": ["prp@SH=insurance", "grp@SH=AIA"]
            },
            "chan": {
                "password": "nahctneitap",
                "attributes": ["pid@SH=001"]
            },
            "koh": {
                "password": "hoktneitap",
                "attributes": ["pid@SH=002"]
            },
            "teo": {
                "password": "oettneitap",
                "attributes": ["pid@SH=003"]
            }
        }
    },
    "MEH": {
        "pk": {
            "aid": "MEH",
            "egga": {
            "type": "pc_element",
            "value": "3:D/2orOzt5X74ZxgFehV12tM06C7CbG/yQ6PCnSho+jAZuykVwQPGzVNcemJqDKZVz38vnT98IJA7Yvcg1CIp6gjzo0hM643n62/irOy3tt0jpGHqJaewhJJfjsvYPBumFzTvEKAId9OzJZ8l90fzPw2dfNm3F+GJf+cwOTIKJREByxpR65oiHaHJi0EnCyz9Y99ut2bXwnbFpOJlgixmuBZc9iD6D1kDIxW8j6g0VjH5QN3NPyM5JfY8r08eMXmIHudX4hNrTjDnfzPq3BkiJ2YTTjvG+4JENSSEmx7indILfG/+RhDFDC219MUHgYK4WlzSPE0Fixt3IOA+1lvUMxuzkds+nr4td7fOecFqEaEop68l9lb5MdAQV8e70OvRFxesizCy6LDbCSVMx+sYo1Hd9IG+CfzMSOqdqAyJ/XoCOapCtBkGrjUkrf88AwX5Y0tmL1N5g7ljSp4DUFg+4BRS4AHPIz5WvhWKN5JY4WXfYS42PxaYwfyEshA8/oQq"
            },
            "gy": {
            "type": "pc_element",
            "value": "1:FZvjky52BXptxrkiMXVcBOiJaMXm+2W82Gxqtep/eT0B"
            }
        },
        "sk": {
            "aid": "MEH",
            "a": {
            "type": "pc_element",
            "value": "0:C/qwZ3U4ynPDPSJN70f1thVLBOHAx3oZvUyRSXjJa8U="
            },
            "y": {
            "type": "pc_element",
            "value": "0:A3H+rd3ayifwS4zBaWA2tKacyuWqEiLrPBAfdKBzPik="
            }
        },
        "users": {
            "tan": {
                "password": "natrotcod",
                "attributes": ["clr@MEH=high"]
            },
            "lee": {
                "password": "eelrotcod",
                "attributes": ["clr@MEH=low", "clr@MEH=med", "clr@MEH=high"]
            },
            "tay": {
                "password": "yatesrun",
                "attributes": ["clr@MEH=low", "clr@MEH=med"]
            },
            "chua": {
                "password": "auhctnegaecnarusni",
                "attributes": ["prp@MEH=insurance", "grp@MEH=AIA"]
            },
            "chan": {
                "password": "nahctneitap",
                "attributes": ["pid@MEH=001"]
            }
        }
    }
}

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Multi-Authority Attribute-based Encryption CLI')
    subparsers = parser.add_subparsers(dest='domain', required=True)

    #######################
    # Attribute Authority #
    #######################
    auth_parser = subparsers.add_parser('auth')
    auth_subparsers = auth_parser.add_subparsers(dest='command', required=True)

    # auth setup
    auth_pubkey_parser = auth_subparsers.add_parser('getpubkey')
    auth_pubkey_parser.add_argument('aid')
    auth_pubkey_parser.add_argument('-o', dest='outfile')

    # auth keygen
    auth_keygen_parser = auth_subparsers.add_parser('keygen')
    auth_keygen_parser.add_argument('aid')
    auth_keygen_parser.add_argument('gid')
    auth_keygen_parser.add_argument('password')
    auth_keygen_parser.add_argument('attrs', nargs='+')
    auth_keygen_parser.add_argument('-o', dest='outfile')

    return parser.parse_args()


def process_arguments(args):

    if args.domain == 'auth':

        if args.command == 'getpubkey':

            pubkey_file = args.outfile or f'{args.aid}.auth'
            with open(pubkey_file, 'w') as f:
                json.dump(serialize(auths[args.aid]['pk']), f, indent=2)

        elif args.command == 'keygen':

            auth = auths[args.aid]

            if(args.password == auth['users'][args.gid]['password']):
                if(set(args.attrs).issubset(auth['users'][args.gid]['attributes'])):
                    keys = RW15.auth_genkeys(gp, auth['sk'], args.gid, args.attrs)

                    keys_file = args.outfile or f'{args.gid}.{auth["sk"]["aid"]}.keys'
                    with open(keys_file, 'w') as f:
                        json.dump(serialize(keys), f, indent=2)

                else:
                    print(args.gid + "does not have the attributes:" + set(args.attrs).difference(auth['users'][args.gid]['attributes']))

            else:
                print("Wrong password")


def main():
    args = parse_arguments()
    process_arguments(args)


if __name__ == '__main__':
    main()
