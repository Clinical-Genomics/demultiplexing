#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --mem=2G
#SBATCH --qos=low
#SBATCH --job-name=demux_on_hasta_S1
#SBATCH --error=/home/proj/development/demux-on-hasta/sbatch_logs/demux.stderr.txt
#SBATCH --output=/home/proj/development/demux-on-hasta/sbatch_logs/demux.stdout.txt
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=barry.stokman@scilifelab.se


conda activate D_demux-on-hasta_BS
bash /home/barry.stokman/development/demultiplexing/scripts/novaseq/checkfornewrun.bash

