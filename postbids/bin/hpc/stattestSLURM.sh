#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH -p hns,normal
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --mem=8GB
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

module load R/3.4.0
module load curl/7.54.0
module load gcc/6.3.0
module load py-scipystack/1.0_py27
module load readline/7.0
# note: I ran these locally (no singularity) because I haven't had time to get rpy in the docker...

python -i $CODEDIR/postbids/restgroup/stattest.py
