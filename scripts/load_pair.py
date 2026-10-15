#!/usr/bin/env python3
"""Read one ground-truth pair and, given the two meshes, check it.

    python scripts/load_pair.py --pair data/PFAUST-M/tr_reg_000_partial_000.pairs.npy \
        --full <FAUST remeshed>/tr_reg_000.off --partial <PFAUST>/PFAUST-M/off/tr_reg_000.off

Without the meshes it only prints the size and the index ranges. With them it
checks that every index is inside its mesh, and for a pair whose two ids are
equal (the partial shape was cut out of that complete shape) it prints the
largest distance between matched vertices, which should be below 1e-7
(3.5e-8, the print precision of the mesh files).
"""
import argparse
import os.path as osp
import re

import numpy as np


def read_off_vertices(path):
    with open(path) as f:
        assert f.readline().strip() == 'OFF', path
        n = int(f.readline().split()[0])
        return np.array([[float(x) for x in f.readline().split()[:3]] for _ in range(n)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pair', required=True, help='a .pairs.npy file (or its .txt export)')
    ap.add_argument('--full', help='the complete mesh, tr_reg_<jjj>.off')
    ap.add_argument('--partial', help='the partial mesh, PFAUST-<V>/off/tr_reg_<iii>.off')
    args = ap.parse_args()

    p = np.load(args.pair) if args.pair.endswith('.npy') else np.loadtxt(args.pair, dtype=np.int64)
    print(f'{osp.basename(args.pair)}: {len(p)} matches, complete indices '
          f'{p[:, 0].min()}..{p[:, 0].max()}, partial indices {p[:, 1].min()}..{p[:, 1].max()}')
    if not (args.full and args.partial):
        return
    Vf, Vp = read_off_vertices(args.full), read_off_vertices(args.partial)
    assert p[:, 0].max() < len(Vf) and p[:, 1].max() < len(Vp), 'index outside the mesh'
    ids = re.findall(r'(\d{3})', osp.basename(args.pair))
    if len(ids) == 2 and ids[0] == ids[1]:
        d = np.linalg.norm(Vf[p[:, 0]] - Vp[p[:, 1]], axis=1)
        print(f'same-id pair: largest distance between matched vertices {d.max():.1e}')
    else:
        print('different ids: the match is semantic, coordinates are not expected to agree')


if __name__ == '__main__':
    main()
