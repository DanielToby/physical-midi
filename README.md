# physical-midi
A CLI to programmatically generate a music box "reel" (stl file) from midi input, for use in a hand-turned music box.

## Dependencies
1. [SDF](https://github.com/fogleman/sdf)https://github.com/fogleman/sdf, a mesh generation library (for constructing the mesh).
2. [Mido]([url](https://mido.readthedocs.io/en/stable/)https://mido.readthedocs.io/en/stable/), a midi object library (for parsing the input).

## Examples
A C major scale as midi input, transposed to accomodate a music box that best matches A major.
```bash
(venv) daniel.toby@US-MA-T2C6V70 physical-midi % python3 generate_cylinder.py -m examples/C-natural_major.mid -f result.stl
Read midi file. Found 15 notes.
Transposed by 21 semitones.
Result will exclude 2 of 15 notes. Continue? [Y/n]
y
min -8.4543, -8.4543, -1.17933
max 8.4543, 8.4543, 20.997
step 0.05, 0.05, 0.05
55663057 samples in 1694 batches with 10 workers
  100% (1694 of 1694) [##############################] 0:00:09 0:00:00    
829 skipped, 278 empty, 587 nonempty
1541340 triangles in 9.13735 seconds
```


The Lick as midi input, whose notes are all supported by the target music box:
```bash
(venv) daniel.toby@US-MA-T2C6V70 physical-midi % python3 generate_cylinder.py -m examples/the_licc.midi -f result.stl
Read midi file. Found 34 notes.
Transposed by 0 semitones.
min -7.59789, -7.77394, -1.17933
max 8.6833, 7.61609, 20.997
step 0.05, 0.05, 0.05
48675984 samples in 1540 batches with 10 workers
  100% (1540 of 1540) [##############################] 0:00:19 0:00:00    
640 skipped, 301 empty, 599 nonempty
1568628 triangles in 19.409 seconds
```
