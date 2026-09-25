# Frontier wave 13 — completed evidence, separate publication gates

## Execution

Two independent fork jobs completed in run:
https://github.com/kvnloo/space-ros/actions/runs/36096339662

Worker revision: `916caae9c68abb608dc470f41ccafb1dbd762b3a`.
No target-repository source was modified. This was not an upstream test suite,
CFD solve, optimization run, browser render, or hardware validation.

## SU2 / existing PR 2865

Public source-trace comment is confirmed posted by kvnloo:
https://github.com/su2code/SU2/pull/2865#issuecomment-5826895661

The new geometry audit used `su2code/TestCases` revision
`790c80ec5b543487b5f8ecf8bb0f0e4d2cc67f3f`, path
`euler/biparabolic/mesh_BIPARABOLIC_sup.su2`, Git blob
`e1e8416171bbbab6b12ca1d1a8b8c8470ae9bff9`.

Observed: 56,831 points, 79,234 cells, and two connected components by node ID
(sizes 52,331 and 4,500). Each nearfield marker has 250 nodes and 249 edges.
There are zero shared node IDs, 250 exact coordinate pairs, no unmatched
coordinates or edges, and no duplicate geometric edges within either marker.
All 249 matched edge pairs have opposing outward normals (relative normal-sum
maximum 0), and each edge has one owning volume cell. The trailing periodic
record is index 0 with zero center, rotation, and translation; the audit checks
this explicitly and rejects nonidentity transforms.

This checks mesh topology and necessary geometric compatibility only. It does
not prove the runtime donor mapping, paired flux exchange, conservation,
uniform-flow preservation, or the cause of the reported divergence.
Do not replace the intended nearfield physics with farfield boundaries to obtain
a green regression. Hold additional public follow-up until useful runtime
validation or maintainer feedback; a geometry follow-up draft is in the handoff.

Artifact: https://github.com/kvnloo/space-ros/actions/runs/36096339662/artifacts/10847407675
ZIP SHA256: `706d2b9ed2dcbf3c5a313a8c68b688ab13869b6c081116305788509b4c4d153a`.

## OpenMDAO / assigned issue 3795

https://github.com/OpenMDAO/OpenMDAO/issues/3795 remains assigned to robfalck.
Evidence-only lane; no competing implementation or PR was started.
Pinned source: `176ac87acb1800fa4e1b5883b4bb73e4890cfe24`, version `3.45.2-dev`.

Actual model execution and HTML generation produced these observed values:

| Case | Existing bound/target fields | Requested driver-scaled values |
| --- | --- | --- |
| Scalar bounds: adder -10, scaler 0.1 | [10, 30] | [0, 2] |
| Vector child lower bounds | [-4, 1] | [-1, 0] |
| Vector child upper bounds | [0, 9] | [0, 16] |
| ref/ref0 constraint bounds | [20, 60] | [0, 1] |
| Equality target: adder -5, scaler 0.2 | 25 | 4 |

Controls confirm scalar model value 20 becomes driver value 1, and constraint
model value 40 becomes driver value 0.5. Existing lower/upper/equals fields and
HTML columns are already present; their tested values are unscaled. The proposed
scope question is explicit model-space versus driver-space bound/equality
columns, not simply adding existing fields.

IMPORTANT: the green verification job proves the five expected baseline
mismatches reproduce. It does NOT mean the requested feature is fixed. No
OpenMDAO source changes, optimization, browser rendering, negative-scaler/unit
conversion tests, or full project/pixi validation was performed. The probe ran
in an isolated venv, not the recommended pixi development environment.

Comment posting was attempted once and returned HTTP403
`Resource not accessible by integration`. No comment was created by that attempt.

Artifact: https://github.com/kvnloo/space-ros/actions/runs/36096339662/artifacts/10847237743
ZIP SHA256: `9986208187abe4176a22f38e4bda099f1512510e911e9674b970a4c887d62c9a`.

## NASA Trick / published PR 2221

https://github.com/nasa/trick/pull/2221 is confirmed open, mergeable, non-draft,
with one commit and two changed files. Do not create another PR.
Upstream CI run https://github.com/nasa/trick/actions/runs/36094161926 has
conclusion `action_required`; no upstream passing-suite claim is made.

## Rejected / corrected worker assumptions

Initial run36096170990 failed in our mesh parser on an unsupported periodic
section. The refined parser accepts only the verified identity metadata and
rejects a nonidentity control. This was a worker limitation, not an SU2 bug.
That initial run also intentionally failed five scaled-bound assertions against
unmodified OpenMDAO; the refined job verifies and preserves that expected failure
rather than changing scientific code or suppressing unexpected errors.

## Policy and concurrency

PlasmaPy remains held for AI-generated upstream contributions. Other untouched
lanes retain wave12's pending policy/ownership gates. These two jobs completed;
there is no claim that 40 workers are running. Manual publication does not block
independent private evidence work.

AI disclosure: ChatGPT generated the research tools, this record, and drafts;
GitHub Actions executed the probes. Both downloaded artifact ZIP hashes were
checked against GitHub's reported SHA256 digests in the ChatGPT sandbox.
