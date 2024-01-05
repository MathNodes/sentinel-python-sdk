# sentinel-python-sdk
A Sentinel SDK Written in Python

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
nodes = sdk.multiquerier.node_querier.QueryNodes(Status.ACTIVE)
subscriptions = sdk.multiquerier.subscription_querier.QuerySubscriptions(pagination=PageRequest(limit=5000, offset=0, reverse=True))
```
