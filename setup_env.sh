module load python/3.11 scipy-stack
ENVDIR=/tmp/$RANDOM
virtualenv --no-download $ENVDIR
source $ENVDIR/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
# run Python script then...
# deactivate
# rm -rf $ENVDIR