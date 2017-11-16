#!/bin/bash
#SBATCH --time=16:00:00
#SBATCH --mem=64GB
#SBATCH -p russpold,hns,normal
#SBATCH --qos=russpold
#SBATCH --output=logs/reduce.txt
#SBATCH --error=logs/reduce.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --cpus-per-task=16
#SBATCH --ntasks=1

#module load R/3.3.0
module load anaconda/anaconda2
source ~/Psychosis/config_sherlock.sh

python /home/jdurnez/Psychosis/06_predictive_model/connectome_reduce.py
