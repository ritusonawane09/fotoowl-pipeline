"""
Agent 5: Compiler & Fixer

Checks whether state["remotion_script"] looks structurally valid, and tracks
retry attempts. This is a STRUCTURAL VALIDATOR (regex/pattern checks), not a
real compiler yet - real Remotion compilation needs Node.js, which we set up
separately (see README "Known limitations"). The interface is designed so
swapping in a real `npx remotion render` check later does not require
changing the graph wiring at all.
"""

import re
from state import PipelineState

REQUIRED_PATTERNS = [
    (r"import\s+.*from\s+['\"]remotion['\"]", "missing import from 'remotion'"),
    (r"<Composition", "missing <Composition> registration"),
    (r"<Sequence", "missing at least one <Sequence> element"),
    (
        r"export\s+(default\s+)?function\s+\w+\s*\(|"
        r"export\s+const\s+\w+(\s*:\s*[^=]+)?\s*=\s*(\([^)]*\)|\w+)\s*=>",
        "missing an exported component function",
    ),
]


def _validate_script(script: str) -> list[str]:
    problems = []
    for pattern, description in REQUIRED_PATTERNS:
        if not re.search(pattern, script):
            problems.append(description)

    if script.count("{") != script.count("}"):
        problems.append(
            f"mismatched curly braces (found {script.count('{')} '{{' vs {script.count('}')} '}}')"
        )

    return problems


def compiler_fixer(state: PipelineState) -> PipelineState:
    script = state.get("remotion_script", "")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)

    problems = _validate_script(script)

    if not problems:
        print(f"  [Compiler] PASSED structural validation (attempt {retry_count + 1})")
        state["compile_success"] = True
        state["compile_error"] = None
        return state

    error_message = "Structural validation failed: " + "; ".join(problems)
    print(f"  [Compiler] FAILED (attempt {retry_count + 1}): {error_message}")

    state["compile_success"] = False
    state["compile_error"] = error_message
    state["retry_count"] = retry_count + 1

    if state["retry_count"] >= max_retries:
        state["pipeline_failed"] = True
        state["failure_reason"] = (
            f"Compiler failed after {max_retries} attempts. Last error: {error_message}"
        )
        print(f"  [Compiler] Hard retry cap ({max_retries}) reached. Exiting gracefully.")

    return state


if __name__ == "__main__":
    good_script = """
import { Composition, Sequence, Img, AbsoluteFill } from 'remotion';

export const EventReel = () => {
  return (
    <Sequence from={0} durationInFrames={90}>
      <Img src="photo1.jpg" />
    </Sequence>
  );
};

export const RemotionRoot = () => {
  return <Composition id="EventReel" component={EventReel} durationInFrames={90} fps={30} width={1080} height={1920} />;
};
"""

    bad_script = """
const EventReel = () => {
  return <div>oops no remotion import, no Composition, mismatched brace {
};
"""

    print("Testing GOOD script:")
    test_state_good: PipelineState = {"remotion_script": good_script, "retry_count": 0, "max_retries": 3}
    result = compiler_fixer(test_state_good)
    print("  compile_success:", result["compile_success"])

    print("\nTesting BAD script:")
    test_state_bad: PipelineState = {"remotion_script": bad_script, "retry_count": 0, "max_retries": 3}
    result = compiler_fixer(test_state_bad)
    print("  compile_success:", result["compile_success"])
    print("  compile_error:", result["compile_error"])
    print("  retry_count:", result["retry_count"])

    print("\nTesting retry cap (simulate 3 consecutive failures):")
    state = {"remotion_script": bad_script, "retry_count": 0, "max_retries": 3}
    for i in range(3):
        state = compiler_fixer(state)
    print("  pipeline_failed:", state.get("pipeline_failed"))
    print("  failure_reason:", state.get("failure_reason"))
