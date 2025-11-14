# FATE Secure Function Component

A third-party FATE component enabling secure computation on encrypted data using homomorphic encryption.

## Overview

This component allows a Guest party to encrypt values and send them to a Host party, which performs computations on the encrypted data without ever seeing the plaintext. Results are returned encrypted and decrypted only by the Guest.

**Key Features:**
- Guest encrypts sensitive data (e.g., columns `x`, `y`)
- Host applies multiple formulas to all data rows without seeing plaintext
- Each formula produces a separate result column
- Results are decrypted only by Guest

**Use Case**: Secure arithmetic operations where one party holds sensitive data and another party has computation formulas that should be applied to all data rows.

## Installation

```bash
cd fate-secure-func
pip install -e .
```

**Verify installation:**
```bash
python -c "from fate_secure_func_client import SecureFunc; print('✓ Installed')"
```

## Quick Start

### 1. Prepare Data

Create test data:
```bash
cd examples
python create_test_data.py
```

Upload to FATE:
```bash
python upload_data.py
```

### 2. Run Pipeline

```bash
python run_pipeline.py
```

### 3. Use in Your Pipeline

```python
from fate_secure_func_client import SecureFunc
from fate_client.pipeline import FateFlowPipeline
from fate_client.pipeline.components.fate import Reader

pipeline = FateFlowPipeline().set_parties(guest=9999, host=10000)

reader = Reader("reader_0")
reader.guest.task_parameters(namespace="experiment", name="guest_values")
reader.hosts[0].task_parameters(namespace="experiment", name="host_formula")

secure_func = SecureFunc(
    "secure_func_0",
    values=reader.guest.outputs["output_data"],
    formula=reader.hosts[0].outputs["output_data"],
    he_param={"kind": "paillier", "key_length": 1024}
)

pipeline.add_tasks([reader, secure_func])
pipeline.compile()
pipeline.fit()
```

## Features

- **Homomorphic Encryption**: Paillier, OU, or Mock schemes
- **Secure Operations**: Add, subtract, multiply by constants on encrypted data
- **Multiple Formulas**: Support computing different formulas per row
- **Easy Integration**: Standard FATE component interface

## Documentation

- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Examples](examples/) - Complete working examples

## Project Structure

```
fate-secure-func/
├── fate_secure_func/          # Server-side component
│   ├── secure_func.py        # Main component entry
│   ├── secure_func_guest.py  # Guest party logic
│   └── secure_func_host.py   # Host party logic
├── fate_secure_func_client/  # Client wrapper
│   └── secure_func.py        # Pipeline API
├── examples/                  # Usage examples
│   ├── create_test_data.py
│   ├── upload_data.py
│   └── run_pipeline.py
└── docs/                      # Documentation
```

## License

MIT License
