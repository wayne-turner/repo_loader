# repo-loader
Walk a repository. Print an ASCII tree. Dump file contents with secrets redacted. Estimate token count. Good for LLM context.

## Features
- **Recursive walk** of a target directory, honoring ignore patterns for build artifacts, VCS folders, binaries, caches, dependencies, media, and more.
- **ASCII tree** representation of the directory hierarchy, with files and subdirectories sorted (README-style files first, then other files, then directories).
- **Content dump** of every file:
  - For text files: prints contents (UTF-8, ignoring errors).
  - For Jupyter notebooks (`.ipynb`): extracts and prints all code cells.
  - For binaries: reports `[Binary file]`.
- **Secret redaction**: automatically replaces common secret patterns (AWS keys, API tokens, JWTs, certs, passwords, database URLs, etc.) with `[REDACTED]`.
- **Extension breakdown**: counts files and lines of code per file extension.
- **Summary report**: total files analyzed, estimated token count (for LLM budgeting), and writes everything out to `context.txt`.


## Requirements
- Python 3.6+
- nbformat


## Usage
By default, the script analyzes the **current working directory**:

```bash
cd /path/to/project
python3 repo_loader.py
```

This will create (or overwrite) a file named `context.txt` in that directory, containing:
1. **Summary** (files analyzed, token estimate)  
2. **ASCII directory tree**  
3. **Contents** of every file (with secrets redacted)

### Import as a module
If you’d rather call it from Python:

```python
from pathlib import Path
from repo_loader import ingest_directory

# Analyze any directory:
summary, tree, contents = ingest_directory(Path("/path/to/target"))

# summary, tree, contents are all strings you can further process.
```



## Output
Sample generated `context.txt`:
```
================================================
Summary
================================================
Directory : tinygrad
Files analyzed : 1123
Estimated tokens : 6,130,970

Files
  .py: 601 files (318,188 lines)
  .h: 48 files (122,461 lines)
  .cuh: 99 files (17,697 lines)
  .ttf: 1 file (10,498 lines)
  .metal: 75 files (9,983 lines)
  .impl: 16 files (8,839 lines)
  .rs: 6 files (4,658 lines)
  .cu: 10 files (4,186 lines)
  .md: 53 files (3,301 lines)
  .s: 3 files (2,543 lines)
  Other: 211 files (22,471 lines)

Tree
└── tinygrad/
    ├── README.md
    ├── setup.py
    ├── .github/
    │   ├── actions/
    │   │   ├── process-replay/
    │   │   │   └── action.yml
    │   │   └── setup-tinygrad/
    │   │       └── action.yml
    │   └── workflows/
    │       ├── autogen.yml
    │       ├── benchmark.yml
    │       └── test.yml
    ├── test/
    │   ├── __init__.py
    │   ├── Dockerfile
    │   ├── helpers.py
    │   └── test_arange.py
    └── tinygrad/
        ├── __init__.py
        ├── device.py
        ├── gradient.py
        ├── tensor.py
        ├── apps/
        │   └── llm.py
        └── viz/
            ├── README
            ├── serve.py
            └── js/
                └── worker.js

================================================
FILE: /home/user/Downloads/tinygrad/README.md
================================================
Despite tinygrad's size, it is a fully featured deep learning framework.
Due to its extreme simplicity, it is the easiest framework to add new accelerators to, with support for both inference and training. 

### Neural networks
As it turns out, 90% of what you need for neural networks are a decent autograd/tensor library.
Throw in an optimizer, a data loader, and some compute, and you have all you need.

## Accelerators
tinygrad already supports numerous accelerators, including:
- [x] [OpenCL](tinygrad/runtime/ops_cl.py)
- [x] [CPU](tinygrad/runtime/ops_cpu.py)
- [x] [METAL](tinygrad/runtime/ops_metal.py)
- [x] [CUDA](tinygrad/runtime/ops_cuda.py)
- [x] [AMD](tinygrad/runtime/ops_amd.py)
- [x] [NV](tinygrad/runtime/ops_nv.py)
- [x] [QCOM](tinygrad/runtime/ops_qcom.py)
- [x] [WEBGPU](tinygrad/runtime/ops_webgpu.py)

...

================================================
FILE: /home/user/Downloads/tinygrad/LICENSE
================================================
Copyright (c) 2024, the tiny corp
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

...

================================================
FILE: /home/user/Downloads/tinygrad/setup.py
================================================
#!/usr/bin/env python3

from pathlib import Path
from setuptools import setup

directory = Path(__file__).resolve().parent
with open(directory / 'README.md', encoding='utf-8') as f:
  long_description = f.read()

testing_minimal = [
  "numpy",
  "torch==2.9.0",
  "pytest",
  "pytest-xdist",
  "pytest-timeout",
  "hypothesis",
  "z3-solver",
]

...
```
