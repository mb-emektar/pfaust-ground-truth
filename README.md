# Dense ground truth for PFAUST

Dense ground-truth correspondences for all **1360 complete–partial pairs** of
the official training and test splits of **PFAUST-M** and **PFAUST-H**.

PFAUST ([Bracha et al.](https://github.com/ABracha/PFAUST)) cuts holes into
the remeshed FAUST shapes. For each partial shape the release records which
vertices of its own complete shape survive, and for each complete shape the
FAUST template correspondence, but not the vertex-to-vertex correspondence
between a partial shape and a *different* complete shape, which training and
evaluating supervised partial matching methods require. Because the partial
meshes are produced by deleting vertices, every partial shape is an exact
vertex subset of the shape it was cut from. We therefore recover the missing
information by matching vertex coordinates between each partial shape and its
complete shape and compose the result with the FAUST template correspondence.
No registration is involved.

The files were produced for the MSc thesis *A Controlled Study of Fan-Based
Mesh Convolution Extensions and Descriptor Masking for Dense Shape
Correspondence* (M. Barış Emektar, Middle East Technical University, 2026).

## Contents

```
data/PFAUST-M/                 680 files: 640 train + 40 test pairs
data/PFAUST-H/                 680 files: 640 train + 40 test pairs
data/pairs_train.txt           the training pairs, one "<full> <partial>" per line
data/pairs_test.txt            the test pairs
scripts/make_gt.py             rebuilds every file from the two public sources
scripts/load_pair.py           reading example and self-check
scripts/export_txt.py          plain-text copy of the files (MATLAB, C++, ...)
```

The meshes are **not** included; they come from their original repositories
(see [Meshes](#meshes)).

## File format

`data/PFAUST-<V>/tr_reg_<jjj>_partial_<iii>.pairs.npy` holds one pair: an
`(N, 2)` array of `int64`, **0-based**.

| column | indexes the vertices of | file in the source repository |
|---|---|---|
| 0 | the complete shape `tr_reg_<jjj>` | FAUST remeshed, `tr_reg_<jjj>.off` |
| 1 | the partial shape cut from `tr_reg_<iii>` | PFAUST, `PFAUST-<V>/off/tr_reg_<iii>.off` |

Row *k* says that vertex `p[k, 0]` of the complete shape corresponds to vertex
`p[k, 1]` of the partial shape. There is one row per FAUST template landmark
that survives in the partial shape, so *N* varies from pair to pair:

| variant | rows per pair (min / mean / max) |
|---|---|
| PFAUST-M | 1673 / 3231 / 4224 |
| PFAUST-H | 1233 / 2697 / 3525 |

Note that the PFAUST repository names its partial meshes `tr_reg_<iii>.off`,
like the complete FAUST shapes. In our file names the first id is always the
complete shape and the second the partial one.

```python
import numpy as np
p = np.load('data/PFAUST-M/tr_reg_080_partial_099.pairs.npy')   # (N, 2)
# with V_full, V_part the vertex arrays of the two meshes:
# V_full[p[:, 0]] are the ground-truth matches of V_part[p[:, 1]]
```

For MATLAB, export a text copy first (`python scripts/export_txt.py`); each
text file has two integers per line and no header, so `p = load(file) + 1`
gives 1-based indices.

## Splits

The official splits of the PFAUST release:

| split | complete shapes | partial shapes | pairs |
|---|---|---|---|
| train | `tr_reg_000, 010, …, 070` | `000 – 079` | 8 × 80 = 640 |
| test | `tr_reg_080, 090` | `080 – 099` | 2 × 20 = 40 |

## Meshes

* Partial shapes: [ABracha/PFAUST](https://github.com/ABracha/PFAUST),
  folders `PFAUST-M/off` and `PFAUST-H/off`.
* Complete shapes and the FAUST template maps (`.vts`): FAUST remeshed from
  [llorz/SGA18_orientation_BCICP_dataset](https://github.com/llorz/SGA18_orientation_BCICP_dataset).

FAUST is distributed under its own license
([faust.is.tue.mpg.de](https://faust.is.tue.mpg.de)); this repository contains
vertex indices only.

## How the files were made

For every partial shape `i` and every complete shape `j` of its split:

1. The partial shape `i` is a vertex subset of the complete shape `tr_reg_<i>`:
   a nearest-neighbour query finds, for every partial vertex, the complete
   vertex at the same position (largest distance about `3.5e-8`, i.e. print
   precision).
2. Inverting this gives, for every vertex of `tr_reg_<i>`, its index in the
   partial shape or "deleted".
3. The FAUST template maps (`.vts`, 5000 landmarks) take landmark *t* to
   vertex `vts_j[t]` of `tr_reg_<j>` and to vertex `vts_i[t]` of `tr_reg_<i>`.
   Landmarks whose vertex survives in the partial shape give one row
   `(vts_j[t], partial index of vts_i[t])`.

`scripts/make_gt.py` does exactly this; run it on the two public sources to
rebuild every file and compare with the ones here.

## Self-check

For a pair with equal ids, e.g. `tr_reg_000_partial_000`, the partial shape was
cut out of the complete one, so every row must point to the same 3D point:

```
python scripts/load_pair.py --pair data/PFAUST-M/tr_reg_000_partial_000.pairs.npy \
    --full <FAUST remeshed>/tr_reg_000.off --partial <PFAUST>/PFAUST-M/off/tr_reg_000.off
```

prints the largest distance between matched vertices, `3.5e-8` (print
precision of the mesh files). A large value means the index base or the mesh
pairing is wrong. For pairs with different ids the match
is semantic, not geometric, and the coordinates do not agree.

## Known imperfection

A few FAUST remeshed vertices are coincident (two vertices at the same
position). Where this happens the coordinate lookup can pick either twin.
Compared with the surviving-vertex lists of the PFAUST release on all 200
partial shapes, the files here agree exactly on 176 shapes and differ on 1–2
landmarks out of about 3000 on the other 24. Both choices are the same 3D
point, so distance-based metrics such as the geodesic error are unaffected.

## Citation

If you use these files, please cite the thesis together with PFAUST and FAUST:

```bibtex
@mastersthesis{emektar2026thesis,
  author = {Emektar, Mustafa Bar{\i}{\c{s}}},
  title  = {A Controlled Study of Fan-Based Mesh Convolution Extensions and
            Descriptor Masking for Dense Shape Correspondence},
  school = {Middle East Technical University},
  year   = {2026}
}

@inproceedings{bracha2023partial,
  author    = {Bracha, Amit and Dag{\`e}s, Thomas and Kimmel, Ron},
  title     = {On Unsupervised Partial Shape Correspondence},
  booktitle = {Asian Conference on Computer Vision (ACCV)},
  pages     = {4488--4504},
  year      = {2024}
}

@inproceedings{bogo2014faust,
  author    = {Bogo, Federica and Romero, Javier and Loper, Matthew and Black, Michael J.},
  title     = {{FAUST}: Dataset and Evaluation for {3D} Mesh Registration},
  booktitle = {IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2014}
}

@article{ren2018continuous,
  author  = {Ren, Jing and Poulenard, Adrien and Wonka, Peter and Ovsjanikov, Maks},
  title   = {Continuous and Orientation-Preserving Correspondences via Functional Maps},
  journal = {ACM Transactions on Graphics},
  volume  = {37},
  number  = {6},
  pages   = {248:1--248:16},
  year    = {2018}
}
```

## License

The correspondence files and the scripts are released under the MIT License
(see `LICENSE`). The meshes they refer to are not part of this repository and
keep the licenses of their sources.
