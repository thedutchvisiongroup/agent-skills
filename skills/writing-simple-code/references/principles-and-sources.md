# Principles and Sources

This skill is independently worded, inspired by Ponytail and established design
principles. These sources explain decisions; they are not runtime dependencies
or instructions to research the entire subject for each task.

## Principles translated into decisions

| Principle | Useful interpretation | Misapplication to avoid |
| --- | --- | --- |
| YAGNI | Build current capabilities; omit speculative options and extension points. | Treating testing, useful refactoring or agreed requirements as unnecessary. |
| KISS | Make behavior and responsibilities straightforward to understand. | Equating simplicity with fewest characters, classes or files. |
| DRY | One authoritative representation of the same domain knowledge. | Combining look-alike code that changes for different reasons. |
| AHA | Abstract a concept after understanding its actual use cases. | A fixed rule that every third copy must become shared code. |
| Simple design | Correct behavior, clear intent and meaningful knowledge ownership precede fewer elements. | Shrinking a diff before understanding the flow. |
| Cohesion and low coupling | Keep related policy together and unrelated reasons to change independent. | Splitting each operation into a pass-through service or treating every layer as bad. |
| Useful encapsulation | A simple interface may hide necessary complexity, even for one caller. | Banning single-caller helpers or single-implementation contracts. |
| SOLID, where relevant | Use fitting OO principles to improve real responsibilities and contracts. | Generating factories, interfaces or containers to satisfy an abstract checklist. |
| Evidence-led optimization | Address supported bounds, requirements and demonstrated bottlenecks. | Adding caching/concurrency for imagined load, or ignoring a clearly unsuitable algorithm. |

These are design heuristics with tradeoffs, not proofs. The skill's binding
requirements are scope discipline, evidence for current complexity, clarification
of consequential uncertainty, and preservation of relevant guarantees.

## Primary design sources

- [Martin Fowler: YAGNI](https://martinfowler.com/bliki/Yagni.html).
  Distinguishes presumptive capabilities from work that keeps code easy to change.
  Explains build, delay, carry and repair costs. YAGNI depends on healthy code.
- [The Pragmatic Programmer: tips](https://pragprog.com/tips/).
  The authors' DRY formulation concerns knowledge (tip 15), not repeated text.
  Independent responsibilities (17), easier-to-change design (14), local scope
  (41) and simplicity (72) support the skill's interpretation.
- [Fowler: Beck's design rules](https://martinfowler.com/bliki/BeckDesignRules.html).
  Correctness, intention, duplication and fewest elements; the article was
  reviewed by Kent Beck. Clarity and duplication sometimes need a balanced choice.
- [Sandi Metz: The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction).
  Shows how superficial reuse becomes conditional, tightly coupled code. Inlining
  a mistaken abstraction can expose the genuine independent responsibilities.
- [Kent C. Dodds: AHA Programming](https://kentcdodds.com/blog/aha-programming).
  Avoid Hasty Abstractions; cautions against dogmatic DRY, WET and occurrence counts.
- [Rich Hickey: Simple Made Easy](https://www.infoq.com/presentations/Simple-Made-Easy/).
  Simplicity means avoiding intertwined concerns, not merely familiarity or small
  counts. Useful encapsulation and abstractions can reduce the mental burden.
- [John Ousterhout: A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)
  and [discussion with Robert Martin](https://github.com/johnousterhout/aposd-vs-clean-code).
  A simple interface hiding substantial functionality can reduce cognitive load.
  This is a counterweight to rigid method-size and anti-abstraction rules.

## Ponytail: inspiration and deliberate differences

[Ponytail's core skill](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md)
encourages necessity checks and reuse before custom code. Its comprehension-first
guidance and [root-cause failure report](https://github.com/DietrichGebert/ponytail/issues/245)
support tracing actual behavior before minimizing a patch.

This skill instead uses behavioral fit rather than a rigid ladder; readable code
rather than one-line preference; agreed scope rather than “ship small, ask later”;
and project/specialist test methods rather than a one-check quota. It has no
runtime modes, prose caps, debt markers or installation hooks. Its instructions
are complementary to a specialist's role and required workflow.

## Evidence limits

- [Independent benchmark criticism](https://github.com/DietrichGebert/ponytail/issues/126)
  identified a chatty baseline and an ambiguous testcase in early results.
- The author's [agentic experiment](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-18-agentic.md)
  reported approximately 54% fewer added lines on twelve tasks, one model and four
  repetitions per task. Feature outputs were counted, not fully exercised in a
  running application. Separate guard checks are not proof of security.
- The author's [comprehension follow-up](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-22-issue-245-217-comprehension.md)
  found model-dependent root-cause improvements; its reuse benefit did not
  reproduce in the selected probes.
- The author's [cost study](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-17-cost-verification.md)
  found that extra instructions increased cost for some reasoning models.

These observations motivate concrete instructions and counterexamples, not
promises of fewer bugs, fixed savings or universal compliance. Static content
review establishes consistency, not actual agent performance. Assess behavior
with fresh representative tasks before making measured effectiveness claims.
