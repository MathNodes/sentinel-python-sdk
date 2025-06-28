# sentinel-python-sdk

A Sentinel SDK Written in Python

## Install

First install the required dependencies:

```shell
sudo apt update
sudo apt install build-essential autoconf automake libtool pkg-config python3-dev
```




This is now a PyPi package and can be installed directly with pip:

```shell
pip install sentinel-sdk
```

### Packaging Python Projects references:

- https://packaging.python.org/en/latest/tutorials/packaging-projects/
- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/

### Development environment:

https://setuptools.pypa.io/en/latest/userguide/development_mode.html

```bash
python -m venv venv
pip install --editable .
```

Please install pre-commit plugin, in order to follow [PEP8](https://peps.python.org/pep-0008/)

```bash
pip install pre-commit
pre-commit install
```

https://pre-commit.com/index.html

### Usage example:

```python
from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import Status, PageRequest
sdk = SDKInstance("grpc.sentinel.co", 9090)
nodes = sdk.nodes.QueryNodes(Status.ACTIVE)
subscriptions = sdk.subscriptions.QuerySubscriptions(pagination=PageRequest(limit=5000, offset=0, reverse=True))
```

## Coded with Love by:

[NAST0R · GitHub](https://github.com/NAST0R) , [Tkd-Alex (Alessandro Maggio) · GitHub](https://github.com/Tkd-Alex), ([freQniK · GitHub](https://github.com/freQniK))

**Commissioned by MathNodes** [MathNodes](https://github.com/MathNodes/sentinel-python-sdk)
