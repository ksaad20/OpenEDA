# OpenEDA
OpenEDA is an AI enabled Electronic Design Automation tool built on Circuit Bench.

# OpenEDA

**AI-powered Electronic Design Automation, open to everyone.**

OpenEDA is an open-source EDA tool that leverages artificial intelligence to automate analog and mixed-signal circuit design. Built on the [Circuit-Bench](https://github.com/ksaad20/Circuit-Bench) benchmark, OpenEDA aims to make professional-grade chip design accessible to researchers, startups, and educators.

---

## Why OpenEDA?

The semiconductor industry relies on a closed triopoly of proprietary EDA tools costing millions per year. This creates a massive barrier to entry for:

- **University researchers** exploring novel architectures
- **Startup chip companies** with limited budgets
- **Educators** training the next generation of designers

OpenEDA changes the equation by providing a free, extensible, AI-driven foundation for circuit design—while remaining compatible with industry-standard workflows and foundry requirements.

---

## Features

- **AI-Assisted Layout**: Generate optimized analog layouts from netlists using reinforcement learning
- **Circuit-Bench Integration**: Evaluate and compare your designs against standardized benchmarks
- **Foundry-Ready Output**: Export to GDSII with DRC/LVS-aware generation
- **Extensible Architecture**: Plugin system for custom devices, PDKs, and optimization objectives
- **Cloud & Local**: Run on your machine or scale via cloud GPU instances

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ksaad20/OpenEDA.git
cd OpenEDA

# Install dependencies
pip install -e .

# Download Circuit-Bench benchmark
python -m openeda.bench download

# Generate an optimized op-amp layout
python -m openeda.layout \
  --netlist examples/ota_2stage.sp \
  --pdk sky130 \
  --output ./layout.gds

# Evaluate on Circuit Bench
python -m openeda.bench evaluate \
  --task analog_layout \
  --model openeda-v0.1 \
  --output results.json

#Architecture
OpenEDA/
├── openeda/
│   ├── layout/          # AI-driven placement & routing
│   ├── sizing/          # Circuit parameter optimization
│   ├── bench/           # Circuit-Bench integration
│   ├── pdk/             # Process design kit interfaces
│   └── models/          # Pre-trained AI models
├── examples/            # Sample circuits and tutorials
├── docs/                # Documentation and API reference
└── tests/               # Test suite

Contributing
We welcome contributions from the community! Whether you are fixing a bug, adding a new PDK, or improving our AI models, your help matters.
Please read our Contributing Guide and Contributor License Agreement before submitting a pull request.

License
OpenEDA is licensed under the Apache License 2.0.
This project includes integration with Circuit-Bench, which is also licensed under Apache 2.0.

| Phase | Target                                   | Status      |
| ----- | ---------------------------------------- | ----------- |
| v0.1  | Core layout engine + Sky130 PDK          | In Progress |
| v0.2  | Circuit-Bench leaderboard integration    | Planned     |
| v0.3  | Cloud execution API                      | Planned     |
| v0.4  | Commercial support & enterprise features | Planned     |


Acknowledgments
Built on Circuit-Bench for standardized evaluation
Inspired by the open-source EDA community: OpenROAD, Magic, KLayout
Supported by [your name/institution/company]

Contact
Issues: GitHub Issues
Discussions: GitHub Discussions
Email: your-kazisaadasif29@gmail.com

OpenEDA: Democratizing chip design, one transistor at a time.
