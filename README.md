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
