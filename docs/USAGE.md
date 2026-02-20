# Usage Guide

## CLI Overview

Proteus provides a structured CLI interface.

Basic syntax:

python main.py generate [options]


---

# Modules

## XSS

python main.py generate --module xss --context html


Contexts:
- html
- attr
- js

---

## SQL Injection

python main.py generate --module sqli --db mysql


Databases:
- mysql
- postgres
- mssql

---

## Command Injection


python main.py generate --module cmd --os linux


Operating Systems:
- linux
- windows

---

# Encoding

--encode base64
--encode hex
--encode url


---

# Obfuscation

--obfuscate comments
--obfuscate whitespace
--obfuscate mixed
--obfuscate case-random


---

# Exporting

## JSON Export

python main.py generate --module xss --context html --export json

##TXT Export

python main.py generate --module sqli --db mysql --export txt


---

# Metadata

Optional metadata:

--meta author=dark run_id=123


---

# Version

python main.py --version


