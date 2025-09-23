import mne
import sys

try:
    file_path = sys.argv[1]
    raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
    print("Available channels:")
    for ch_name in raw.ch_names:
        print(f"- {ch_name}")
except Exception as e:
    print(f"Error: {e}")
