# API Reference

## Client API

### SecureFunc

Pipeline component for secure function computation.

```python
from fate_secure_func_client import SecureFunc

secure_func = SecureFunc(
    name="secure_func_0",
    values=reader.guest.outputs["output_data"],
    formula=reader.hosts[0].outputs["output_data"],
    he_param={"kind": "paillier", "key_length": 1024}
)
```

**Parameters:**

- `name` (str): Component instance name
- `values` (DataframeInput): Encrypted data from guest party
- `formula` (DataframeInput): Computation formulas from host party
- `he_param` (dict): Homomorphic encryption parameters
  - `kind` (str): Encryption scheme - `"paillier"`, `"ou"`, or `"mock"`
  - `key_length` (int): Key size in bits (1024, 2048, 3072, or 4096)

**Returns:**
- Guest output: DataFrame with original columns plus one result column per formula
  - Input: N rows × M columns
  - Output: N rows × (M + number_of_formulas) columns
- Host output: None

---

## Server Components

### SecureFuncGuest

Guest party implementation handling encryption and decryption.

#### `__init__(ctx: Context)`

Initialize encryption kit (Paillier/OU/Mock).

#### `encrypt_and_send(values: DataFrame)`

Encrypt DataFrame columns and send to host.

**Process:**
1. Extract columns from DataFrame
2. Encrypt each column using PHE
3. Send encrypted data + public key to host

#### `receive_and_decrypt() -> DataFrame`

Receive encrypted results and decrypt.

**Returns:**
- DataFrame with original data + decrypted result columns
- One new column per formula from host
- Column names match formula IDs (e.g., `formula_0`, `formula_1`)

---

### SecureFuncHost

Host party performing computations on encrypted data.

#### `__init__(ctx)`

Receive encryption kit (public key + evaluator) from guest.

#### `eval(formula: DataFrame)`

Compute formulas on encrypted data.

**Supported Operations:**
- Addition: `x+y`
- Subtraction: `x-y`
- Scalar multiplication: `2*x+3*y`

**Process:**
1. Receive encrypted values from guest (all rows)
2. For each formula, perform homomorphic operations on all data rows
3. Send encrypted results back to guest (one column per formula)

**Important:** Each formula in the host's DataFrame is applied to **all rows** of the guest's data, producing a separate result column.

---

## How It Works

### Data Flow

1. **Guest** has 8 rows of data with columns `x` and `y`
2. **Host** has 4 formulas to compute
3. Result: Guest gets 8 rows with 4 additional result columns

### Computation Matrix

```
Guest Data (8 rows):        Host Formulas (4):
┌────┬───┬───┐              ┌──────────┬─────────┐
│ id │ x │ y │              │ id       │ formula │
├────┼───┼───┤              ├──────────┼─────────┤
│id_0│ 3 │ 5 │              │formula_0 │ x+y     │
│id_1│ 5 │ 8 │              │formula_1 │ x-y     │
│id_2│ 7 │ 2 │    ──►       │formula_2 │ x+y     │
│id_3│ 1 │ 4 │              │formula_3 │ x-y     │
│id_4│ 4 │ 7 │              └──────────┴─────────┘
│id_5│ 6 │ 3 │
│id_6│ 8 │ 9 │
│id_7│ 2 │ 6 │
└────┴───┴───┘

Result (8 rows × 7 columns):
┌────┬───┬───┬──────────┬──────────┬──────────┬──────────┐
│ id │ x │ y │formula_0 │formula_1 │formula_2 │formula_3 │
├────┼───┼───┼──────────┼──────────┼──────────┼──────────┤
│id_0│ 3 │ 5 │    8     │    -2    │    8     │    -2    │
│id_1│ 5 │ 8 │   13     │    -3    │   13     │    -3    │
│id_2│ 7 │ 2 │    9     │     5    │    9     │     5    │
│id_3│ 1 │ 4 │    5     │    -3    │    5     │    -3    │
│id_4│ 4 │ 7 │   11     │    -3    │   11     │    -3    │
│id_5│ 6 │ 3 │    9     │     3    │    9     │     3    │
│id_6│ 8 │ 9 │   17     │    -1    │   17     │    -1    │
│id_7│ 2 │ 6 │    8     │    -4    │    8     │    -4    │
└────┴───┴───┴──────────┴──────────┴──────────┴──────────┘
```

**Key Points:**
- Each formula is applied to **all guest rows**
- Results form a matrix: N_rows × N_formulas
- All computation happens on encrypted data
- Host never sees plaintext values

---

## Data Formats

### Guest Input (values)

CSV with columns to encrypt. The `id` column is used as match key:

```csv
id,x,y
id_0,3,5
id_1,5,8
id_2,7,2
id_3,1,4
id_4,4,7
id_5,6,3
id_6,8,9
id_7,2,6
```

**Note:** 
- `id`: Match ID column (string format like `id_0`, `id_1`, etc.)
- `x`, `y`: Numeric columns to be encrypted and computed

### Host Input (formula)

CSV with formulas. Each formula will be applied to all guest data rows:

```csv
id,formula
formula_0,x+y
formula_1,x-y
formula_2,x+y
formula_3,x-y
```

**Note:**
- `id`: Formula identifier (e.g., `formula_0`, `formula_1`)
- `formula`: Expression to compute (supports `x+y`, `x-y`, `2*x+3*y`, etc.)
- Each formula is computed for **all rows** in guest data

### Guest Output (result)

Original data + computed results for each formula:

```csv
id,x,y,formula_0,formula_1,formula_2,formula_3
id_0,3,5,8,-2,8,-2
id_1,5,8,13,-3,13,-3
id_2,7,2,9,5,9,5
id_3,1,4,5,-3,5,-3
id_4,4,7,11,-3,11,-3
id_5,6,3,9,3,9,3
id_6,8,9,17,-1,17,-1
id_7,2,6,8,-4,8,-4
```

**Output Structure:**
- Original columns preserved: `id`, `x`, `y`
- New columns added: One column per formula (`formula_0`, `formula_1`, etc.)
- Each cell contains the result of applying that formula to that row's data

---

## Encryption Schemes

### Paillier (Recommended)

Additive homomorphic encryption supporting addition and scalar multiplication.

```python
he_param = {"kind": "paillier", "key_length": 1024}
```

**Key Lengths:** 1024 (fast), 2048 (balanced), 3072/4096 (secure)

### OU (Okamoto-Uchiyama)

Alternative additive HE scheme.

```python
he_param = {"kind": "ou", "key_length": 1024}
```

### Mock (Testing Only)

No encryption - for testing pipeline logic.

```python
he_param = {"kind": "mock", "key_length": 1024}
```

---

## Example Usage

### Complete Pipeline

```python
from fate_client.pipeline import FateFlowPipeline
from fate_client.pipeline.components.fate import Reader
from fate_secure_func_client import SecureFunc

# Create pipeline
pipeline = FateFlowPipeline().set_parties(guest=9999, host=10000)

# Read data
reader = Reader("reader_0")
reader.guest.task_parameters(namespace="experiment", name="guest_values")
reader.hosts[0].task_parameters(namespace="experiment", name="host_formula")

# Secure computation
secure_func = SecureFunc(
    "secure_func_0",
    values=reader.guest.outputs["output_data"],
    formula=reader.hosts[0].outputs["output_data"],
    he_param={"kind": "paillier", "key_length": 2048}
)

# Execute
pipeline.add_tasks([reader, secure_func])
pipeline.compile()
pipeline.fit()

# Get results
result = pipeline.get_task_info("secure_func_0").get_output_data()
print(result)
```

---

## Security Notes

1. **Key Length**: Use 2048+ bits for production
2. **Mock Mode**: Never use in production - no encryption
3. **Data Leakage**: Host never sees plaintext values
4. **Formula Privacy**: Guest doesn't know host's formulas

---

## See Also

- [Examples](../examples/) - Working code examples
- [README](../README.md) - Quick start guide
