import mne
import neurokit2 as nk
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import os
from mne.preprocessing import ICA

def analyze_ecg_with_ica(file_path):
    """
    Uses ICA to extract a clean ECG signal from multi-channel abdominal recordings
    and then performs a full HRV and arrhythmia analysis.
    """
    try:
        print(f"Loading data from '{file_path}'...")
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
        sampling_rate = raw.info['sfreq']

        # 1. Pick only the abdominal channels for ICA
        abd_channels = [ch for ch in raw.ch_names if 'Abdomen' in ch]
        if len(abd_channels) < 2:
            print("Error: ICA requires at least 2 channels. Found fewer than 2 abdominal channels.")
            return
        print(f"Found {len(abd_channels)} abdominal channels for ICA: {abd_channels}")
        raw.pick(abd_channels)

        # 2. Filter the data before ICA
        print("Filtering data (1-40 Hz)...")
        raw.filter(l_freq=1.0, h_freq=40.0, fir_design='firwin', verbose=False)

        # 3. Apply ICA
        print("Applying Independent Component Analysis (ICA)...")
        ica = ICA(n_components=len(abd_channels), max_iter='auto', random_state=97)
        ica.fit(raw)

        # 4. Automatically find the ECG component
        print("Finding ECG component among ICA sources...")
        ecg_indices, scores = ica.find_bads_ecg(raw, method='ctps', threshold=0.8)
        
        if not ecg_indices:
            print("\n--- ICA ANALYSIS FAILED ---")
            print("Could not automatically identify a clear ECG component from the mixed signals.")
            print("This indicates the signal quality is too low even for advanced separation techniques.")
            # For debugging, save the ICA sources
            ica.plot_sources(raw, show=False).savefig("ica_sources.png")
            print("Plot of all separated sources saved to 'ica_sources.png' for manual inspection.")
            return

        ecg_source_index = ecg_indices[0]
        print(f"Successfully identified component {ecg_source_index} as the main ECG source.")

        # 5. Get the clean ECG signal from the identified source
        print("Reconstructing clean ECG signal from the identified source...")
        ecg_reconstructed = ica.get_sources(raw).get_data(picks=ecg_source_index).ravel()

        # 6. Run the full analysis on the reconstructed clean signal
        print("Running full analysis on the reconstructed signal...")
        signals, info = nk.ecg_process(ecg_reconstructed, sampling_rate=sampling_rate, method="pantompkins1985")

        if "R_Peaks" not in info or len(info["R_Peaks"]) < 5:
            print("\n--- ANALYSIS FAILED ON RECONSTRUCTED SIGNAL ---")
            print("Even after ICA, not enough R-peaks were detected.")
            nk.ecg_plot(signals, info)
            plt.savefig("final_analysis_plot.png")
            print("Plot of the final analysis attempt saved to 'final_analysis_plot.png'.")
            return

        # --- Full Analysis Output ---
        print("\n--- SUCCESS: FULL ECG ANALYSIS COMPLETE ---")
        hrv = nk.hrv(info['R_Peaks'], sampling_rate=sampling_rate)
        print("\nHeart Rate Variability (HRV) Metrics:")
        print(hrv)

        poincare_filename = "poincare_plot.png"
        nk.poincare_plot(info['R_Peaks'])
        plt.savefig(poincare_filename)
        print(f"\nPoincare plot saved to '{poincare_filename}'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Use ICA to analyze ECG data from a multi-channel EDF file.")
    parser.add_argument("file_path", help="The absolute path to the .edf file.")
    args = parser.parse_args()
    
    if args.file_path:
        analyze_ecg_with_ica(file_path=args.file_path)
    else:
        parser.print_help()
