# VLM Advisor (Module 4)

A vision-language model that looks directly at site imagery/the reconstructed
3D scene *and* at the structured outputs the other modules already produce
(`ElementStatus`, `SafetyAlert`, schedule data), narrates what is built,
missing, wrong, or still needed, and holds an actual back-and-forth
conversation with the user about it -- not a one-shot report generator.

## Why it is Module 4, not a bolt-on

It has to run on phone-class hardware and medium-spec laptops/desktops, the
same constraint Module 3 (edge deployment) already exists to solve. This
rules out hosted-API-only designs and large open VLMs as the default path:
whatever model is chosen has to be small enough to quantize and export
through the same ONNX/TensorRT/OpenVINO pipeline as the detector/tracker/depth
models. See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) section 2 for how this
cross-references Module 3.

## Inputs

- Imagery / reconstructed scene: raw site photos and/or the aligned point
  cloud or rendered BIM overlay from Module 1 (recon).
- Structured state: `ElementStatus`, `SafetyAlert`, and schedule data per
  [INTERFACES.md](INTERFACES.md).

## Interaction

Conversational: the user can ask follow-up questions and discuss findings,
not just receive a generated summary. Exact interface (CLI chat, app, or
otherwise) is not yet decided.

## Open for discussion

These are deliberately left open -- decide and update this doc (and
[INTERFACES.md](INTERFACES.md)) once settled:

- **Replace vs. augment**: does the VLM replace the rule-based
  `ElementStatus`/`SafetyAlert` comparison as the source of truth, or does it
  sit on top of and narrate/discuss conclusions the rule-based logic still
  produces? This decides whether the advisor is a new *producer* of status
  (needing its own contract in `INTERFACES.md`) or just a *consumer* of the
  existing one.
- **Local-only vs. pluggable API backend**: local-model-only keeps the
  pipeline fully self-contained and open-source per the project's stated
  goals; a pluggable design that can also call a hosted API trades that off
  against capability and needs secrets handling (API keys) the rest of the
  pipeline doesn't currently require.

## Candidate models (not yet chosen)

Needs a genuinely small/efficient open VLM -- large open models (LLaVA-34B,
Qwen2-VL-72B class) will not fit the phone/medium-laptop constraint even
quantized. Scope this once the two open questions above are settled.
