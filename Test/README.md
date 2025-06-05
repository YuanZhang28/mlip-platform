
# MLIP vs. VASP ΔE Benchmark Tool

This tool benchmarks Machine Learning Interatomic Potentials (MLIPs) such as SevenNet against VASP-calculated DFT reference data, specifically for delithiated cathode structures.

It compares predicted and reference ΔE values using the formula:

```
ΔE = E(structure) + n_Li × E(Li) - E(Ref)
```

## 🔧 Features

- Extracts energy and forces using ASE from VASP `OUTCAR` and MLIP `CONTCAR`
- Computes ΔE from both DFT and MLIP
- Reports force magnitudes and convergence flags
- Outputs a summary `.csv` file

## 📦 Requirements

Install dependencies via pip:

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python benchmark.py --main_dir ./example_data --li_dir ./example_data/Li --mlip_model 7net-mf-ompa
```

### Arguments

- `--main_dir`: Folder containing `00_ref/`, `45/`, `46/`, ..., `56/`
- `--li_dir`: Folder with lithium reference (`CONTCAR`, `OUTCAR`)
- `--mlip_model`: SevenNet model name (default: `7net-mf-ompa`)
- `--output_csv`: Output filename (default: `deltaE_with_forces.csv`)

## 📁 Example Folder Structure

```
example_data/
├── 00_ref/
│   ├── OUTCAR
│   └── CONTCAR
├── 45/
│   ├── OUTCAR
│   └── CONTCAR
└── Li/
    ├── OUTCAR
    └── CONTCAR
```

## 📝 Output

- `deltaE_with_forces.csv` — table of ΔE comparisons, force magnitudes, convergence flags

## 👤 Author

Marcus Neo (forked & modified by request)
