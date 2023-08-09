# physical-midi
A CLI to programmatically generate 3D meshes from midi input, for use in a hand-cranked music box.

## Dependencies
1. [SDF](https://github.com/fogleman/sdf)https://github.com/fogleman/sdf, a mesh generation library (for constructing the mesh).
2. [Mido]([url](https://mido.readthedocs.io/en/stable/)https://mido.readthedocs.io/en/stable/), a midi object library (for parsing the input).

## Goals
1. Provided a cheap music box (they all conform roughly to the same design), remove the cheap set screw that holds the cylinder in place with an M6 equivalent.
2. Write a Python script that:
    - programmatically generates the 20mm tall cylinder mesh (constructed along the positive Z axis).
    - consumes midi files and converts these into a series of `Pin` representations, each consisting of a Z-height and an angle theta.
    - generates a series of 0.6mm cubic bumps along the exterior of the mesh that strike the tines of the music box.
3. 3D print the resulting meshes with a material that satisfies the resolution and durability requirements. Formlabs' Rigid 10k Resin for SLA printing achieves the resolution, but rigid resins can be brittle. SLS printing produces very durable parts, but achieving such fine features can be challenging.

## Examples
A C major scale as midi input, passed to a music box whose tines form an incomplete A major scale several octaves higher:
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


A Jazz lick as midi input, whose notes are all supported by the target:
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
