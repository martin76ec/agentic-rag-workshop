# Exercises — Track A "Build it"

Each part ships **runnable but broken** code. You run it, see the bad output,
fix the TODOs, and re-run until tests pass.

```
exercises/
├── part1_plain/     45 min  — chunking · top-k · prompt
├── part2_graph/     60 min  — neighborhood · blast radius · fusion
└── part3_agentic/   75 min  — triage · router · state · specialist
```

## How to run

```bash
make exercise 1.1     # run broken code on kafka-broker, then run tests
make check    1.1     # run only the tests
make solution 1.1     # copy reference solution over the broken file (escape hatch)
```

`N.M` follows the file numbering inside each part. Read the part's `README.md`
before starting.

## Reference solutions

The full reference implementation lives in `src/`. After completing each
exercise, diff your fix against the corresponding `src/` file to see how the
project actually wires it up.
