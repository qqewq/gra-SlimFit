https://orcid.org/my-orcid?orcid=0009-0004-1872-1153
https://doi.org/10.5281/zenodo.19782810
# SlimFit GRA: Weight Loss Without Hunger via GRA Nullification

This repository implements a multilevel GRA nullification experiment for generating personalized diet plans that minimize subjective hunger while achieving weight loss.

## Quick Start

```bash
pip install -r requirements.txt
python examples/run_slimfit.py
```

Or explore interactively:

```bash
jupyter notebook notebooks/exploration.ipynb
```

## How It Works

Three levels of GRA foam are minimized simultaneously:

- **Static** — final weight, fat percentage, muscle preservation, metabolic rate.
- **Cyclic** — daily hunger oscillation amplitude and peak hunger.
- **Chaotic** — weight variance, frequency of high-hunger days, and plateaus.

A genetic algorithm evolves daily calorie, protein, and fiber intake over the diet period. A simplified metabolic model simulates weight change and composition; a hunger predictor estimates subjective hunger.

## Structure

- `gra_slimfit/` — core modules (foam, metabolism, hunger, optimizer)
- `examples/` — run script
- `notebooks/` — Jupyter exploration
- `tests/` — unit tests
- `paper/` — LaTeX article

## License

MIT
