# Problem quality benchmark

Decides whether a problem pack is good enough to practise on. Java only.
Needs Python 3.10+, `javac` and `java`. No other dependencies.

```bash
python3 bench/problem_bench.py                     # all catalog problems
python3 bench/problem_bench.py my_problem --harder # gate a new problem
python3 bench/problem_bench.py my_problem --verbose # list every uncaught bug
python3 bench/problem_bench.py --calibrate         # re-measure the shipped problems
```

Exit code is 0 only when every checked problem is accepted. A full run of ten
problems takes about seven minutes on two cores; one problem takes under a
minute. Results are cached until the solution or the cases change.

## Adding a problem

A problem is `problems/<id>/{spec,cases,hidden}/level1-4.*` plus
`langs/java/problems/<id>/{solution,stub}.java`. Register it once, then gate it:

```bash
python3 bench/register_problem.py <id>
python3 bench/problem_bench.py <id> --harder
```

Registering edits `langs/catalog.json` and `src/honepad/workstub.py`. Honepad's
own pytest suite (`make check`) was written for the ten shipped problems in
every language and may report failures once a Java-only problem is in the
catalog; this has not been tested. Practising is unaffected.

## What it checks

| Gate | Fails when |
|---|---|
| files present | a spec, cases, hidden, solution or stub file for levels 1-4 is missing |
| case schema | ids repeat, level tags are wrong, values are not null/bool/int/string/list |
| registered | the problem is not in `langs/catalog.json` or `workstub.py` `_CLASS` |
| level progression | a level adds no new method, hidden cases call a locked method, or a spec never names its new method |
| hidden differs from public | a hidden case repeats a public one |
| java sources | a method is missing, or the solution uses randomness, the clock, files or the network |
| test volume | fewer than 3 public cases or 6 hidden calls in a level |
| solution passes every case | the reference solution fails any public or hidden case |
| spec examples match solution | an example line in a spec disagrees with what the solution returns |
| stub compiles and fails | the starting stub does not compile, or already passes over 25% of cases |
| test strength | too few injected bugs are caught (see below) |
| novelty | over 50% of the method names match another problem |
| harder than baseline (`--harder`) | the solution is not larger and more branching than the top quarter of shipped problems |

## Test strength

The benchmark makes up to 40 one-token bugs in the reference solution (`<` to
`<=`, `&&` to `||`, `+` to `-`, a constant off by one, a dropped `!`) and runs
the tests against each. The score is the share of bugs some test catches. A
bug no test catches is printed with its line number: that is the case to add.

Some injected bugs cannot change behaviour, so 100% is not always reachable.
The bar is capped at 90% for that reason.

## Bars

`baseline.json` holds the bars and the measurements they came from.
`--calibrate` rewrites it from the ten shipped problems:

- bugs caught by public + hidden tests: at least the shipped median
- bugs caught by public tests alone: at least the shipped lower quartile
- `--harder`: decision points and code lines at least the shipped upper quartile

Do not run `--calibrate` after adding your own problems unless you pass only
the original ten ids, or the bars will drift toward your additions.

## Spec example convention for new problems

Each `spec/levelN.md` needs at least one fenced block of lines shaped like
`method(args) -> value`, with JSON values, that works top to bottom from an
empty system. The benchmark replays it against the solution. Four shipped
problems predate this and are reported as warnings instead.

## What it cannot tell you

It does not read the spec for clarity, and it does not know whether a problem
is interesting. A problem can pass every gate and still be badly worded.
