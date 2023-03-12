# CS442 Group Project: Cloud-based EMR System w/ dABE

## References
KP-ABE: https://eprint.iacr.org/2006/309.pdf
BSW07 CP-ABE: https://www.cs.utexas.edu/~bwaters/publications/papers/cp-abe.pdf
W11 CP-ABE: https://eprint.iacr.org/2008/290.pdf
LW11 dCP-ABE: https://eprint.iacr.org/2010/351.pdf
RW15 dCP-ABE: https://eprint.iacr.org/2015/016.pdf

MOH Useful Links: https://www.moh.gov.sg/hpp/all-healthcare-professionals/useful-links
Healthcare Professionals Database: https://www.moh.gov.sg/hpp/all-healthcare-professionals/healthcare-professionals-search
CDC Data: https://www.cdc.gov/DataStatistics/

## Setup

### Prerequisites
* Python 3.7 (does not work with conda, may not work with other versions)

### Installation

1. Clone the [charm repository](https://github.com/JHUISI/charm)
```bash
git clone https://github.com/JHUISI/charm.git
cd charm
```

2. Install dependencies
```bash
sudo apt install build-essential flex bison m4 python3.7-dev python3.7-distutils python3.7-setuptools libgmp-dev libssl-dev
pip install -r requirements.txt
./configure
cd ./deps/pbc && make && sudo ldconfig
cd -
```

4. Build charm
```bash
make && sudo make install && sudo ldconfig
```

5. Test installation
```bash
sudo make test
```

6. Copy the `charm` subfolder to the root of this repository
