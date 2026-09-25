# Frontier upstream gates — wave 12

A successful scout or test job is NOT contribution-policy approval. Read complete
current CONTRIBUTING, AI policy, inherited guidance, and templates before preparing
an upstream submission. A file named AGENTS.md is not permission to submit generated
contributions. Only an explicitly reviewed task may enter the publication queue.

## Holds

- **PlasmaPy/PlasmaPy — HOLD_AI_CONTRIBUTION_POLICY.** CONTRIBUTING.md at
  391579b61d153bfe4b92f59f39ab6e563a44f29d says the project cannot currently accept
  significant AI-generated contributions. Both planned lanes (#3285, #3310) leave
  the AI-upstream queue. The already-completed fork-only example exercise is
  learning-only; do not submit its candidate, report, or an AI-generated comment.
  https://github.com/PlasmaPy/PlasmaPy/blob/391579b61d153bfe4b92f59f39ab6e563a44f29d/CONTRIBUTING.md
- **idaholab/moose — POLICY_SCAN_INCOMPLETE.** The scout's recursive tree exceeded
  its response-size cap. Use targeted reads before selecting an implementation.
- **PX4/PX4-Autopilot — READ_LINKED_AI_POLICY_FIRST.** Follow its Assisted-by commit
  trailer format and restrictions; do not apply a universal PR disclosure footer.
- **AVSLab/basilisk — HUMAN_REVIEW_REQUIRED.** Check full current contributor AI
  requirements and secure genuine human review; never imply Kevin performed an
  unverified review. Both originally selected issues were closed in the scout.

## Other lanes

All other lanes still require task-specific policy/ownership review; absence of an
AI-specific file is not automatic approval. SU2 #2865 is an existing contributor's
PR; provide source evidence and coordinate, not a competing rewrite. Keep the
nearfield/equivalent-area physics intact. Source tracing is not CFD validation.

## Confirmed scout output

20 repositories, 40 candidates, 223 GETs, 4 concurrent readers. 10 candidates
closed; 6 assigned; 1 existing PR; 1 discovery-only; 22 open pending review. These
are raw scout categories, prior to applying the policy holds above.

## Workflow change

Remove PlasmaPy from subsequent wave-12 automatic runs. Preserve the completed
8-example-check result as personal learning, not upstream-ready work. Do not
count self-tests or documentation examples as flight, plasma-model, or solver
validation. No new upstream issue or PR was created during this wave.
