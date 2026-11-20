#!/bin/bash
set -e
cd "$(dirname "$0")"
for base in "$HOME/anaconda3" "$HOME/miniconda3" "$HOME/miniforge3" /opt/anaconda3 /opt/miniconda3; do
  if [ -f "$base/etc/profile.d/conda.sh" ]; then source "$base/etc/profile.d/conda.sh"; break; fi
done
conda activate ai_wps
python -m streamlit run app.py
