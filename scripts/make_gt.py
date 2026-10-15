#!/usr/bin/env python3
"""Rebuild the PFAUST ground-truth pair files from the two public sources.

Inputs
    --partial-dir   PFAUST-<V>/off of https://github.com/ABracha/PFAUST,
                    holding the partial meshes tr_reg_000.off ... tr_reg_099.off
    --faust-shapes  the remeshed FAUST complete shapes tr_reg_000.off ... (from
                    https://github.com/llorz/SGA18_orientation_BCICP_dataset)
    --faust-vts     the FAUST template maps tr_reg_000.vts ... of the same
                    dataset (5000 rows each, 1-based vertex indices)
    --out           output folder, e.g. data/PFAUST-M

Output
    <out>/tr_reg_<jjj>_partial_<iii>.pairs.npy, an (N, 2) int64 array, 0-based:
    column 0 indexes the complete shape tr_reg_<jjj>, column 1 the partial
    shape cut from tr_reg_<iii>. One file per pair of the official splits:
        train  complete 000, 010, ..., 070  x  partial 000 ... 079   (640)
        test   complete 080, 090            x  partial 080 ... 099   ( 40)

Method
    1. The partial shape i is a vertex subset of the complete shape tr_reg_<i>
       (PFAUST deletes vertices, nothing is moved), so a nearest-neighbour query
       maps every partial vertex to the complete vertex at the same position.
       The script stops if any distance exceeds 1e-6.
    2. Inverting this map gives, for every vertex of tr_reg_<i>, its index in
       the partial shape or -1 if the vertex was deleted.
    3. Template landmark t is vertex vts_j[t] of tr_reg_<j> and vertex vts_i[t]
       of tr_reg_<i>. Landmarks that survive in the partial shape give the row
       (vts_j[t], partial index of vts_i[t]).

    Coincident vertices: a few FAUST remeshed vertices share one position, and
    step 2 then keeps one of the twins. This changes 1-2 of about 3000 rows on
    24 of the 200 partial shapes; both twins are the same 3D point.

    python scripts/make_gt.py --partial-dir PFAUST/PFAUST-M/off \
        --faust-shapes FAUST_r/off --faust-vts FAUST_r/corres --out data/PFAUST-M

Optional: --partial-name sets the file name pattern of the partial meshes
(default tr_reg_{:03d}.off, as in the PFAUST repository).
"""
import argparse
import os
import os.path as osp

import numpy as np
from scipy.spatial import cKDTree

SPLITS = {
    'train': (list(range(0, 80, 10)), list(range(0, 80))),
    'test': ([80, 90], list(range(80, 100))),
}
SUBSET_TOL = 1e-6


def read_off_vertices(path):
    with open(path) as f:
        assert f.readline().strip() == 'OFF', path
        n = int(f.readline().split()[0])
        return np.array([[float(x) for x in f.readline().split()[:3]] for _ in range(n)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--partial-dir', required=True)
    ap.add_argument('--faust-shapes', required=True)
    ap.add_argument('--faust-vts', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--partial-name', default='tr_reg_{:03d}.off')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    def vts(i):
        return np.loadtxt(osp.join(args.faust_vts, f'tr_reg_{i:03d}.vts'), dtype=np.int64) - 1

    for split, (full_ids, partial_ids) in SPLITS.items():
        vts_full = {j: vts(j) for j in full_ids}
        for i in partial_ids:
            Vp = read_off_vertices(osp.join(args.partial_dir, args.partial_name.format(i)))
            Vf = read_off_vertices(osp.join(args.faust_shapes, f'tr_reg_{i:03d}.off'))
            d, sub2full = cKDTree(Vf).query(Vp)
            assert d.max() < SUBSET_TOL, f'partial {i:03d} is not a vertex subset ({d.max():.2e})'
            full2sub = np.full(len(Vf), -1, dtype=np.int64)
            full2sub[sub2full] = np.arange(len(Vp))
            c = full2sub[vts(i)]
            keep = c >= 0
            for j in full_ids:
                pairs = np.stack((vts_full[j][keep], c[keep]), axis=1)
                np.save(osp.join(args.out, f'tr_reg_{j:03d}_partial_{i:03d}.pairs.npy'), pairs)
        print(f'{split}: {len(full_ids)} complete x {len(partial_ids)} partial = '
              f'{len(full_ids) * len(partial_ids)} files -> {args.out}')


if __name__ == '__main__':
    main()
