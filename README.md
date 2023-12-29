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

### Usage example:
```python
from sentinel_sdk.sdk import SDKInstance
my_sdk = SDKInstance("grpc.sentinel.co", 9090)
my_sdk.multiquerier.node_querier.QueryNodes()
```

