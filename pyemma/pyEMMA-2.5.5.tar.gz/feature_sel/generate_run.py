
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--lag', default=500)
parser.add_argument('--dest', default='run.sh')
args = parser.parse_args()

template = """#!/bin/bash

#SBATCH --job-name=final_lag_{lag}
#SBATCH -D /home/marscher/NO_BACKUP/final_lag_{lag}
#SBATCH --output=logs/cache_feat_%A_%a.out
#SBATCH --time=1-0
#SBATCH --mem=250000M
#SBATCH --cpus-per-task=24
#SBATCH --partition=big
#SBATCH --array 0-167
#SBATCH --export=PYTHONUNBUFFERED=1
#SBATCH --mail-type=fail
#SBATCH --mail-user=m.scherer@fu-berlin.de

export OMP_NUM_THREADS=$SLURM_CPUS_ON_NODE
/home/marscher/miniconda3/envs/cov_/bin/python /home/marscher/feature_sel/analysis/calc_cov_single_feat.py \
   --output=/home/marscher/NO_BACKUP/final_lag_{lag} --lag={lag} $SLURM_ARRAY_TASK_ID
""".format(lag=args.lag)

with open(args.dest, 'w') as f:
    f.write(template)
