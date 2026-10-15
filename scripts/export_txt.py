#!/usr/bin/env python3
"""Write a plain-text copy of every pair file, for MATLAB, C++ or anything
without numpy.

    python scripts/export_txt.py [--src data] [--out data_txt]

<out>/PFAUST-<V>/full_<jjj>__partial_<iii>.txt holds two integers per line,
"<complete index> <partial index>", 0-based, no header. The numbers are copied
unchanged from data/PFAUST-<V>/tr_reg_<jjj>_partial_<iii>.pairs.npy.
In MATLAB:  p = load('full_080__partial_099.txt') + 1;   % 1-based
"""
import argparse
import glob
import os
import os.path as osp
import re

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='data')
    ap.add_argument('--out', default='data_txt')
    args = ap.parse_args()
    n = 0
    for f in sorted(glob.glob(osp.join(args.src, 'PFAUST-*', 'tr_reg_*_partial_*.pairs.npy'))):
        variant = osp.basename(osp.dirname(f))
        j, i = re.match(r'tr_reg_(\d+)_partial_(\d+)\.pairs\.npy', osp.basename(f)).groups()
        os.makedirs(osp.join(args.out, variant), exist_ok=True)
        np.savetxt(osp.join(args.out, variant, f'full_{j}__partial_{i}.txt'), np.load(f), fmt='%d')
        n += 1
    print(f'wrote {n} text files to {args.out}')


if __name__ == '__main__':
    main()
