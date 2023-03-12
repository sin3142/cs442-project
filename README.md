# CS442 Group Project: Cloud-based EMR System w/ dABE

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
