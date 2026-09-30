# fleet-skills

Turn a directory of personal helper scripts into self-describing agent skills:
a generated `SKILL.md` per script (purpose, args, env names, exit codes, safety
classification) plus a uniform `fleet` CLI to discover, inspect, and safely run them.

- **Python 3.12, stdlib only, fully offline.** No network calls, no daemons, no listeners.
- All run state lives in `~/.fleet/runs.jsonl`; generated skills live in `skills/`.

## Install (pip-less, just PATH)

```sh
# one file, no dependencies:
cp fleet ~/bin/fleet        # or: sudo cp fleet /usr/local/bin/fleet
chmod +x ~/bin/fleet
fleet --version
```

`fleet` is a single ~500-line Python script. It reads scripts, never phones home.

## Commands

| Command | What it does |
|---|---|
| `fleet scan [dir]` | Find executable scripts (`*.sh`, `*.py`) and cron definitions; print a table. **Writes nothing.** |
| `fleet gen [dir] --out skills/` | Generate one `SKILL.md` per script + a `SKILLS.md` registry. |
| `fleet run <skill> [--dry-run] [-- args...]` | Run a skill. `--dry-run` prints the exact command without executing. Every real run appends one JSON line to `~/.fleet/runs.jsonl`. |
| `fleet list` | List skills in the registry. |
| `fleet show <skill>` | Print a skill's `SKILL.md`. |

Global flag: `--skills-dir DIR` (or `$FLEET_SKILLS`) to point `run`/`list`/`show`
at a different skills directory. Default: `./skills`.

## Safety model

Every script is classified by an extensible heuristic list (`SAFETY_HEURISTICS`
at the top of `fleet` — add your own regexes there):

- `read-only` — no writes detected.
- `writes-files` — touches the filesystem, a DB, containers, etc.
- `destructive` — `rm -rf`, `DROP TABLE`, `podman rm`, `mkfs`, `kill -9`, …

A skill classified **destructive** refuses to run unless its skill directory
contains an empty file named `ALLOW_DESTRUCTIVE`. Only variable **names** are
ever recorded — secret values are never printed or stored.

## Worked example 1 — document and run a read-only toy

The `examples/` directory ships two toy scripts. Document them:

```sh
cd ~/workspace/fleet-skills

# 1. Survey first — scan never writes anything
./fleet scan examples
# SKILL NAME   KIND    SAFETY       DESCRIPTION
# toy-clean    script  destructive  toy_clean.sh — DESTRUCTIVE DEMO: recursively delete …
# toy-read     script  read-only    Count lines and words in a text file and print a one…

# 2. Generate the skills (into a scratch dir, so the real registry is untouched)
./fleet gen examples --out /tmp/demo-skills
# Generated 2 skills in /tmp/demo-skills (+ SKILLS.md registry)

# 3. Read what fleet learned about the script
./fleet --skills-dir /tmp/demo-skills show toy-read
```

`SKILL.md` for `toy-read` records its `--file`/`--top` flags, the `TOY_DATA_DIR`
env name, and exit codes `0/1/2` — all extracted from the source. Now run it,
first as a dry-run, then for real:

```sh
echo "hello fleet" > /tmp/demo.txt

./fleet --skills-dir /tmp/demo-skills run toy-read --dry-run -- --file /tmp/demo.txt --top 1
# dry-run: /home/hatch/workspace/fleet-skills/examples/toy_read.py --file /tmp/demo.txt --top 1

./fleet --skills-dir /tmp/demo-skills run toy-read -- --file /tmp/demo.txt --top 1
# /tmp/demo.txt: 1 lines, 2 words
#   | hello fleet

# every real run is logged:
tail -1 ~/.fleet/runs.jsonl
# {"ts": "2026-09-30T01:15:09+00:00", "skill": "toy-read",
#  "args": ["--file", "/tmp/demo.txt"], "exit": 0}
```

## Worked example 2 — the destructive gate

`toy-clean.sh` contains `rm -rf`, so fleet classifies it destructive:

```sh
./fleet --skills-dir /tmp/demo-skills run toy-clean --dry-run -- /tmp/scratch
# fleet: REFUSED — skill 'toy-clean' is classified destructive.
# fleet: create an empty file named ALLOW_DESTRUCTIVE in the skill directory to allow it.

# Opt in explicitly, per skill:
touch /tmp/demo-skills/toy-clean/ALLOW_DESTRUCTIVE

./fleet --skills-dir /tmp/demo-skills run toy-clean --dry-run -- /tmp/scratch
# dry-run: /home/hatch/workspace/fleet-skills/examples/toy_clean.sh /tmp/scratch

# Remove the marker when done to restore the safe default:
rm /tmp/demo-skills/toy-clean/ALLOW_DESTRUCTIVE
```

## Scanning the real fleet

```sh
./fleet scan ~/workspace        # 19 scripts, 31 cron definitions
./fleet gen ~/workspace --out skills
./fleet list                    # registry view
```

Cron definitions (files under `cron.d/` / `crons/` trees, or with "cron" in the
name) are listed by scan for awareness; `gen` documents scripts only.

## Extending the safety heuristics

Open `fleet` and add entries to `SAFETY_HEURISTICS` — `(regex, class)` pairs,
first match wins, checked destructive → writes-files → read-only default.
