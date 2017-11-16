#!/bin/bash
#SBATCH --job-name=PSY_XTRACT
#SBATCH --output=/home/jdurnez/Psychosis/00_server_to_local/logs/psychosis_import.out
#SBATCH --error=/home/jdurnez/Psychosis/00_server_to_local/logs/psychosis_import.err
#SBATCH --time=24:00:00
#SBATCH --mem=64GB
#SBATCH --partition=russpold,hns,normal
#SBATCH --qos=russpold
#SBATCH --mail-type=ALL
#SBATCH --mail-user=joke.durnez@gmail.com
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16

source $HOME/Psychosis/config_sherlock.sh

cd $DICOMDIR/import
wget http://olinnidb.org/download/NIDB-1416.zip

python $CODEDIR/00_server_to_local/extract_and_organise.py
