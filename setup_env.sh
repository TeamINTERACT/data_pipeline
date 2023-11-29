# Run in data_pipeline dir
module list
module load python/3.11 scipy-stack 
module list
source /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/venv_py311_scipystack/bin/activate
module load proj # Need to be loaded once venv activated
module list
pip install --no-index --upgrade pip
pip install -r /home/btcrchum/projects/def-dfuller/btcrchum/data_pipeline/requirements.txt
