
import os
import numpy as np
import pandas as pd
from ase.io import read
from ase.calculators.sevennet import SevenNetCalculator

# Function to extract energy, maximum force, and convergence info from a structure file
def extract_energy_and_force(path, format="vasp", calculator=None):
    atoms = read(path, format=format)
    if calculator:
        atoms.calc = calculator
    energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    max_force = np.linalg.norm(forces, axis=1).max()
    converged = atoms.info.get("converged", "Unknown")
    return energy, max_force, converged

# Main benchmark function to loop through system directories and calculate ΔE comparisons
def run_benchmark(main_dir, li_dir, model_name='7net-mf-ompa', output_csv="deltaE_with_forces.csv"):
    results = []

    # Initialize SevenNet MLIP calculator
    calc = SevenNetCalculator(model_name, modal='mpa')

    # Load Li reference structure (single lithium configuration)
    li_path = os.path.join(li_dir, "CONTCAR")
    li_outcar = os.path.join(li_dir, "OUTCAR")
    energy_li_ml, max_force_li_ml, _ = extract_energy_and_force(li_path, calculator=calc)
    energy_li_vasp, max_force_li_vasp, _ = extract_energy_and_force(li_outcar)

    # Load fully lithiated reference structure
    ref_dir = os.path.join(main_dir, "00_ref")
    ref_contcar = os.path.join(ref_dir, "CONTCAR")
    ref_outcar = os.path.join(ref_dir, "OUTCAR")
    energy_ref_ml, max_force_ref_ml, _ = extract_energy_and_force(ref_contcar, calculator=calc)
    energy_ref_vasp, max_force_ref_vasp, converged_ref = extract_energy_and_force(ref_outcar)

    # Loop through folders like '45', '46', etc. representing number of Li removed
    for folder in os.listdir(main_dir):
        if not folder.isdigit():
            continue  # skip non-numeric folders

        n_li_removed = int(folder)
        folder_path = os.path.join(main_dir, folder)
        contcar_path = os.path.join(folder_path, "CONTCAR")
        outcar_path = os.path.join(folder_path, "OUTCAR")

        try:
            # Extract VASP energy and forces from OUTCAR
            energy_vasp, max_force_vasp, converged_vasp = extract_energy_and_force(outcar_path)

            # Extract MLIP energy and forces from CONTCAR
            energy_ml, max_force_ml, _ = extract_energy_and_force(contcar_path, calculator=calc)

            # Calculate ΔE using VASP and MLIP
            deltaE_vasp = energy_vasp + n_li_removed * energy_li_vasp - energy_ref_vasp
            deltaE_ml = energy_ml + n_li_removed * energy_li_ml - energy_ref_ml
            delta_diff = deltaE_ml - deltaE_vasp

            # Store result for this configuration
            results.append({
                "System": folder,
                "n_Li_removed": n_li_removed,
                "VASP ΔE (eV)": deltaE_vasp,
                "SevenNet ΔE (eV)": deltaE_ml,
                "Δ (MLIP - VASP)": delta_diff,
                "Max Force (VASP)": max_force_vasp,
                "Max Force (MLIP)": max_force_ml,
                "VASP Converged?": converged_vasp
            })
        except Exception as e:
            print(f"[ERROR] {folder}: {e}")

    # Output results to CSV and print to terminal
    df = pd.DataFrame(results).sort_values("n_Li_removed")
    df.to_csv(output_csv, index=False)
    print(df.to_string(index=False))

# Entry point with command-line interface
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark MLIP vs VASP for delithiated structures")
    parser.add_argument('--main_dir', required=True, help='Path to main directory containing 00_ref and folders like 45, 46...')
    parser.add_argument('--li_dir', required=True, help='Path to Li reference directory')
    parser.add_argument('--mlip_model', default='7net-mf-ompa', help='SevenNet model name')
    parser.add_argument('--output_csv', default='deltaE_with_forces.csv', help='Output CSV filename')
    args = parser.parse_args()

    run_benchmark(args.main_dir, args.li_dir, args.mlip_model, args.output_csv)

if __name__ == "__main__":
    main()
