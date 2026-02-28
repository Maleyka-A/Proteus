# Proteus

Educational Offensive Payload Template Framework (Non-Executing)

Proteus is a modular, safety-focused payload template generation framework designed for secure coding education, detection engineering practice, and authorized security research environments.

---

## Disclaimer

Proteus generates inert, non-executing payload templates only.

The framework:

- Does not perform exploitation  
- Does not execute commands  
- Does not establish network connections  
- Does not interact with databases  
- Does not send HTTP requests  
- Does not contain weaponized payload logic  

All outputs are structured string templates intended strictly for:

- Authorized penetration testing labs  
- Academic learning  
- Defensive research  
- Security training environments  

This project aligns with OWASP ethical standards and internship task scope requirements.

---

## Project Objective

Proteus was developed to demonstrate:

- How common web vulnerability patterns are structured  
- How security controls (WAFs, filters, validators) detect patterns  
- How encoding and obfuscation alter payload representations  
- Why secure coding practices eliminate these risks  

The emphasis is on education, architecture clarity, and defensive understanding.

---

## Supported Modules

### XSS (Context-Aware Templates)

Generates template markers demonstrating:

- Reflected XSS concepts  
- Stored XSS concepts  
- DOM-based XSS concepts  

Supported contexts:

- html  
- attr  
- js  

All templates include defensive guidance and are non-executing by design.

---

### SQL Injection (Simulation Templates)

Generates structured templates for:

- Error-based concepts  
- Union-based concepts  
- Blind (boolean/time-based) concepts (descriptive markers only)  
- Filter evasion concepts (case/comment behavior explanation)

Supported database selectors:

- mysql  
- postgres  
- mssql  

No database interaction is performed.

---

### Command Injection (Pattern-Based Templates)

Generates conceptual templates for:

- Command injection fundamentals  
- Command separator concepts  
- Filter evasion discussion  
- OS detection logic concepts  

Supported OS selectors:

- linux  
- windows  

All command patterns are marker-based and disabled by default.

---

## Architecture Overview

Proteus is structured with clear separation of responsibilities.

### core/models.py

Strongly validated `PayloadTemplate` model:

- Module-specific selector enforcement  
- Risk level classification  
- Tagging support  
- UTC timestamping  
- Safety flag enforcement (`disabled_by_default=True`)  
- Export-safe serialization methods  

### core/registry.py

Decorator-based plugin system:

- Dynamic module registration  
- Selector validation  
- Type enforcement for generator outputs  

### core/pipeline.py

Execution orchestration:

1. Template generation  
2. Optional encoding  
3. Optional obfuscation  
4. Optional export  

### transforms/

Representation-only transformations:

- Encoding: url, base64, hex  
- Obfuscation: comments, whitespace, mixed  

Obfuscation is restricted to explicit educational templates containing marker identifiers.

### exporters/

Offline catalog export:

- JSON exporter (schema wrapper, deterministic ordering, atomic write)  
- TXT exporter (human-readable catalog, atomic write)  

---

## Project Structure

```bash
.
├── cli.py
├── config.py
├── core/
│   ├── models.py
│   ├── pipeline.py
│   └── registry.py
├── modules/
│   ├── xss.py
│   ├── sqli.py
│   └── cmd_injection.py
├── transforms/
│   ├── encoder.py
│   └── obfuscator.py
├── exporters/
│   ├── json_exporter.py
│   └── txt_exporter.py
├── docs/
│   ├── ETHICS.md
│   └── USAGE.md
├── tests/
│   ├── test_cli.py
│   ├── test_encoder.py
│   ├── test_exporters.py
│   ├── test_modules.py
│   └── test_pipeline.py
└── pyproject.toml
```
# Installation
```
git clone https://github.com/Maleyka-A/Proteus
cd Proteus
```
### Create a virtual environment:
```
python -m venv venv
source venv/bin/activate
```
### Run the CLI:
```
python main.py --version
```
### If installed as a console script:
```
proteus --version
```
## CLI Usage
### Basic syntax:
```
python main.py generate [options]
```
### XSS Example:
```
python main.py generate --module xss --context html
```
### SQL Injection Example:
```
python main.py generate --module sqli --db mysql
```
### Command Injection Example:
```
python main.py generate --module cmd --os linux
```
---
## Encoding (Representation Only)
Supported encodings: url,base64,hex.
```
python main.py generate --module xss --context html --encode base64
```
---
## Obfuscation (Education-Only Guardrails)
Supported modes: comment, whitespace,mixed.
Obfuscation is restricted to educational template markers.
```
python main.py generate --module xss --context html --obfuscate mixed
```
---
## Exporting
JSON Export
```
python main.py generate --module xss --context html --export json --output samples/output.json
```
TXT Export
```
python main.py generate --module sqli --db mysql --export txt --output samples/output.txt
```
---
## Metadata
```
python main.py generate --module xss --context html --export json --meta author=dark run_id=123
```
---
## Testing
```
pytest -v
```
Coverage includes:
- CLI validation
- Encoding correctness
- Export safety enforcement
- Module selector validation
- Pipeline orchestration
- Error handling
---
## Safety Principles
Proteus is intentionally constrained:
- All outputs are marker-based templates
- _disabled_by_default=True_ is enforced at model and export layers
- No dynamic execution (eval, exec)
- No subprocess invocation
- No HTTP or database clients
- No automatic request sending
The framework is designed for defensive learning and architectural clarity.
---
## Author
MALEYKA AGHAYEVA
