#!/usr/bin/env python3
"""Create and grade local devark skill eval fixtures."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


EVALS_PATH = Path(__file__).resolve().parent / "evals.json"

ARK_TEMPLATE = """#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OHOS_ROOT = Path(__file__).resolve().parent
LOG_PATH = OHOS_ROOT / ".devark_eval_build.json"
SPECS_PATH = OHOS_ROOT / "mock_build_specs.json"


def read_text(path):
    try:
        return path.read_text()
    except OSError:
        return ""


def evaluate_checks(checks):
    results = []
    ok = True
    for check in checks:
        target = OHOS_ROOT / check["path"]
        passed = False
        evidence = ""
        if check["op"] == "exists":
            passed = target.exists()
            evidence = "exists" if passed else "missing"
        elif check["op"] == "contains":
            content = read_text(target)
            passed = check["needle"] in content
            evidence = check["needle"] if passed else "missing: " + check["needle"]
        elif check["op"] == "contains_any":
            content = read_text(target)
            passed = any(needle in content for needle in check["needles"])
            evidence = "matched one of needles" if passed else "missing all alternative needles"
        else:
            evidence = "unsupported check op: " + check["op"]
        ok = ok and passed
        results.append({
            "path": check["path"],
            "op": check["op"],
            "passed": passed,
            "evidence": evidence,
        })
    return ok, results


def record(status, target, args, checks, failures):
    payload = {
        "status": status,
        "target": target,
        "args": args,
        "cwd": str(Path.cwd()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "failures": failures,
    }
    LOG_PATH.write_text(json.dumps(payload, indent=2))


def main():
    args = sys.argv[1:]
    target = None
    if len(args) >= 2:
        for arg in args[1:]:
            if not arg.startswith("--"):
                target = arg
                break

    if not target:
        record("error", None, args, [], ["missing target"])
        print("mock ark.py: missing target", file=sys.stderr)
        return 2

    specs = json.loads(SPECS_PATH.read_text())
    spec = specs.get(target)
    if not spec:
        record("error", target, args, [], ["unknown target"])
        print(f"mock ark.py: unknown target {target}", file=sys.stderr)
        return 2

    ok, checks = evaluate_checks(spec.get("checks", []))
    failures = [f"{item['path']} ({item['op']})" for item in checks if not item["passed"]]
    status = "ok" if ok else "failed"
    record(status, target, args, checks, failures)
    if not ok:
        print("mock ark.py: verification failed", file=sys.stderr)
        for item in failures:
            print(f" - {item}", file=sys.stderr)
        return 1

    print(f"mock ark.py: build succeeded for {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


FIXTURES = {
    0: {
        "slug": "clamp-warmup-count",
        "build_target": "clamp_warmup_countJitAction",
        "expected_branch": "main",
        "plan_contains": ["ClampWarmupCount"],
        "doc_names": ["warmup_counter.md"],
        "task_progress": "Progress: 1/1 completed",
        "artifact_paths": [
            "ecmascript/interpreter/warmup_counter.h",
            "ecmascript/interpreter/warmup_counter.cpp",
            "test/jittest/BUILD.gn",
            "test/jittest/clamp_warmup_count/BUILD.gn",
            "test/jittest/clamp_warmup_count/clamp_warmup_count.ts",
            "test/jittest/clamp_warmup_count/expect_output.txt",
        ],
        "build_checks": [
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/ecmascript/interpreter/warmup_counter.cpp",
                "needle": "count < 0",
            },
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/ecmascript/interpreter/warmup_counter.cpp",
                "needle": "count > 10",
            },
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/test/jittest/BUILD.gn",
                "needle": "clamp_warmup_count:clamp_warmup_countJitAction",
            },
            {
                "op": "exists",
                "path": "arkcompiler/ets_runtime/test/jittest/clamp_warmup_count/clamp_warmup_count.ts",
            },
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/test/jittest/clamp_warmup_count/expect_output.txt",
                "needle": "10",
            },
        ],
        "project_files": {
            "ecmascript/interpreter/warmup_counter.h": """
                #ifndef ECMASCRIPT_INTERPRETER_WARMUP_COUNTER_H
                #define ECMASCRIPT_INTERPRETER_WARMUP_COUNTER_H

                #include <cstdint>

                namespace panda::ecmascript {
                class WarmupCounter {
                public:
                    static int32_t ClampWarmupCount(int32_t count);
                };
                }  // namespace panda::ecmascript

                #endif  // ECMASCRIPT_INTERPRETER_WARMUP_COUNTER_H
            """,
            "ecmascript/interpreter/warmup_counter.cpp": """
                #include "ecmascript/interpreter/warmup_counter.h"

                namespace panda::ecmascript {
                int32_t WarmupCounter::ClampWarmupCount(int32_t count)
                {
                    return count;
                }
                }  // namespace panda::ecmascript
            """,
            "test/test_helper.gni": """
                template("host_jit_test_action") {
                }
            """,
            "test/jittest/BUILD.gn": """
                group("ark_jit_ts_test") {
                  deps = [ "base_smoke:base_smokeJitAction" ]
                }
            """,
            "test/jittest/base_smoke/BUILD.gn": """
                import("//arkcompiler/ets_runtime/test/test_helper.gni")

                host_jit_test_action("base_smoke") {
                }
            """,
            "test/jittest/base_smoke/base_smoke.ts": """
                declare function print(arg: any): string;

                print("base");
            """,
            "test/jittest/base_smoke/expect_output.txt": """
                Copyright (c) 2026 Huawei Device Co., Ltd.
                Licensed under the Apache License, Version 2.0 (the "License");
                you may not use this file except in compliance with the License.
                You may obtain a copy of the License at

                    http://www.apache.org/licenses/LICENSE-2.0

                Unless required by applicable law or agreed to in writing, software
                distributed under the License is distributed on an "AS IS" BASIS,
                WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                See the License for the specific language governing permissions and
                limitations under the License.
                base
            """,
        },
    },
    1: {
        "slug": "resume-normalize-tagged-value",
        "build_target": "normalize_tagged_valueJitAction",
        "expected_branch": "main",
        "plan_contains": ["NormalizeTaggedValue", "existing plan"],
        "doc_names": ["tagged_value_utils.md", "normalize_tagged_value.md"],
        "task_progress": "Progress: 1/1 completed",
        "artifact_paths": [
            "ecmascript/interpreter/tagged_value_utils.h",
            "ecmascript/interpreter/tagged_value_utils.cpp",
            "test/jittest/BUILD.gn",
            "test/jittest/normalize_tagged_value/BUILD.gn",
            "test/jittest/normalize_tagged_value/normalize_tagged_value.ts",
            "test/jittest/normalize_tagged_value/expect_output.txt",
        ],
        "build_checks": [
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/ecmascript/interpreter/tagged_value_utils.cpp",
                "needle": "value < 0",
            },
            {
                "op": "contains_any",
                "path": "arkcompiler/ets_runtime/ecmascript/interpreter/tagged_value_utils.cpp",
                "needles": ["value % 2", "value & 1"],
            },
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/test/jittest/BUILD.gn",
                "needle": "normalize_tagged_value:normalize_tagged_valueJitAction",
            },
            {
                "op": "exists",
                "path": "arkcompiler/ets_runtime/test/jittest/normalize_tagged_value/normalize_tagged_value.ts",
            },
            {
                "op": "contains",
                "path": "arkcompiler/ets_runtime/test/jittest/normalize_tagged_value/expect_output.txt",
                "needle": "8",
            },
        ],
        "project_files": {
            "ecmascript/interpreter/tagged_value_utils.h": """
                #ifndef ECMASCRIPT_INTERPRETER_TAGGED_VALUE_UTILS_H
                #define ECMASCRIPT_INTERPRETER_TAGGED_VALUE_UTILS_H

                #include <cstdint>

                namespace panda::ecmascript {
                class TaggedValueUtils {
                public:
                    static int32_t NormalizeTaggedValue(int32_t value);
                };
                }  // namespace panda::ecmascript

                #endif  // ECMASCRIPT_INTERPRETER_TAGGED_VALUE_UTILS_H
            """,
            "ecmascript/interpreter/tagged_value_utils.cpp": """
                #include "ecmascript/interpreter/tagged_value_utils.h"

                namespace panda::ecmascript {
                int32_t TaggedValueUtils::NormalizeTaggedValue(int32_t value)
                {
                    // TODO: negative values should map to 0 and odd positives should round up.
                    return value;
                }
                }  // namespace panda::ecmascript
            """,
            "test/test_helper.gni": """
                template("host_jit_test_action") {
                }
            """,
            "test/jittest/BUILD.gn": """
                group("ark_jit_ts_test") {
                  deps = [ "normalize_tagged_value:normalize_tagged_valueJitAction" ]
                }
            """,
            "test/jittest/normalize_tagged_value/BUILD.gn": """
                import("//arkcompiler/ets_runtime/test/test_helper.gni")

                host_jit_test_action("normalize_tagged_value") {
                }
            """,
            "test/jittest/normalize_tagged_value/normalize_tagged_value.ts": """
                declare function print(arg: any): string;

                print("TODO");
            """,
            "test/jittest/normalize_tagged_value/expect_output.txt": """
                Copyright (c) 2026 Huawei Device Co., Ltd.
                Licensed under the Apache License, Version 2.0 (the "License");
                you may not use this file except in compliance with the License.
                You may obtain a copy of the License at

                    http://www.apache.org/licenses/LICENSE-2.0

                Unless required by applicable law or agreed to in writing, software
                distributed under the License is distributed on an "AS IS" BASIS,
                WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                See the License for the specific language governing permissions and
                limitations under the License.
                0
                4
                8
            """,
        },
        "resume_files": {
            ".agents/devark/main/plan.md": """
                # Plan

                ## Goal
                Finish the existing NormalizeTaggedValue task without replacing the task history.

                ## Scope
                - Keep work on the current branch
                - Reuse the existing `.agents/devark/main/` task tracker
                - Land the runtime fix, docs update, review, and build verification
            """,
            ".agents/devark/main/tasks.md": """
                # Tasks

                ## Task 1: tagged_value_utils
                - [x] Write failing test (TS + C++)
                - [ ] Write implementation
                - [ ] Format & commit
                - Status: in_progress
                - Reason: Continue the unfinished NormalizeTaggedValue task

                ---
                Progress: 0/1 completed
            """,
        },
    },
}


def load_eval_prompts() -> dict[int, dict]:
    data = json.loads(EVALS_PATH.read_text())
    return {int(item["id"]): item for item in data["evals"]}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def run_cmd(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        args,
        cwd=str(cwd),
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def flatten_name(path: str) -> str:
    return path.replace("/", "__")


def evaluate_checks(repo_root: Path, checks: list[dict]) -> list[dict]:
    results = []
    for check in checks:
        target = repo_root / check["path"]
        passed = False
        evidence = ""
        if check["op"] == "exists":
            passed = target.exists()
            evidence = "exists" if passed else "missing"
        elif check["op"] == "contains":
            content = target.read_text() if target.exists() else ""
            passed = check["needle"] in content
            evidence = check["needle"] if passed else f"missing `{check['needle']}`"
        elif check["op"] == "contains_any":
            content = target.read_text() if target.exists() else ""
            passed = any(needle in content for needle in check["needles"])
            evidence = "one alternative matched" if passed else "missing all alternative needles"
        else:
            evidence = f"unsupported op {check['op']}"
        results.append(
            {
                "text": f"{check['op']} {check['path']}",
                "passed": passed,
                "evidence": evidence,
            }
        )
    return results


def create_repo(run_dir: Path, fixture: dict) -> dict:
    repo_root = run_dir / "repo" / "ohos"
    project_root = repo_root / "arkcompiler" / "ets_runtime"
    project_root.mkdir(parents=True, exist_ok=True)
    (repo_root / "out" / "x64.debug").mkdir(parents=True, exist_ok=True)

    write_text(repo_root / "ark.py", ARK_TEMPLATE)
    (repo_root / "ark.py").chmod(0o755)

    for rel_path, content in fixture["project_files"].items():
        write_text(project_root / rel_path, content)

    for rel_path, content in fixture.get("resume_files", {}).items():
        write_text(project_root / rel_path, content)

    write_json(
        repo_root / "mock_build_specs.json",
        {
            fixture["build_target"]: {
                "checks": fixture["build_checks"],
            }
        },
    )

    run_cmd(["git", "init", "-b", fixture["expected_branch"]], repo_root)
    run_cmd(["git", "config", "user.name", "Devark Eval"], repo_root)
    run_cmd(["git", "config", "user.email", "devark-eval@example.com"], repo_root)
    run_cmd(["git", "add", "."], repo_root)
    run_cmd(["git", "commit", "-m", "chore: seed devark eval fixture"], repo_root)

    return {
        "repo_root": str(repo_root),
        "project_root": str(project_root),
    }


def setup_workspace(workspace: Path, iteration: int) -> None:
    prompts = load_eval_prompts()
    iteration_dir = workspace / f"iteration-{iteration}"
    if iteration_dir.exists():
        shutil.rmtree(iteration_dir)
    iteration_dir.mkdir(parents=True)

    for eval_id, fixture in FIXTURES.items():
        prompt = prompts[eval_id]
        eval_dir = iteration_dir / f"eval-{eval_id}-{fixture['slug']}"
        write_json(
            eval_dir / "eval_metadata.json",
            {
                "eval_id": eval_id,
                "eval_name": fixture["slug"],
                "prompt": prompt["prompt"],
                "assertions": [],
            },
        )

        for config in ("with_skill", "without_skill"):
            run_dir = eval_dir / config / "run-1"
            repo_info = create_repo(run_dir, fixture)
            actual_prompt = prompt["prompt"].replace("<PROJECT_ROOT>", repo_info["project_root"])
            write_json(
                run_dir / "eval_metadata.json",
                {
                    "eval_id": eval_id,
                    "eval_name": fixture["slug"],
                    "prompt": actual_prompt,
                    "assertions": [],
                },
            )
            spec = deepcopy(fixture)
            spec.update(repo_info)
            spec["config"] = config
            spec["expected_output"] = prompt["expected_output"]
            write_json(run_dir / "fixture_spec.json", spec)


def collect_outputs(run_dir: Path, duration_ms: int, total_tokens: int) -> None:
    spec = json.loads((run_dir / "fixture_spec.json").read_text())
    repo_root = Path(spec["repo_root"])
    project_root = Path(spec["project_root"])
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    current_branch = run_cmd(["git", "branch", "--show-current"], repo_root).strip()
    write_json(
        outputs_dir / "run_info.json",
        {
            "current_branch": current_branch,
            "build_target": spec["build_target"],
            "config": spec["config"],
            "repo_root": str(repo_root),
            "project_root": str(project_root),
        },
    )
    write_json(
        run_dir / "timing.json",
        {
            "total_tokens": total_tokens,
            "duration_ms": duration_ms,
            "total_duration_seconds": round(duration_ms / 1000.0, 3),
        },
    )

    git_status = run_cmd(["git", "status", "--short"], repo_root)
    git_log = run_cmd(["git", "log", "--oneline", "--decorate", "-5"], repo_root)
    git_show = run_cmd(["git", "show", "--stat", "--oneline", "HEAD"], repo_root)
    write_text(outputs_dir / "git_status.txt", git_status or "(clean)")
    write_text(outputs_dir / "git_log.txt", git_log)
    write_text(outputs_dir / "git_show_stat.txt", git_show)

    build_log = repo_root / ".devark_eval_build.json"
    if build_log.exists():
        shutil.copy2(build_log, outputs_dir / "build_result.json")

    plan_base = None
    agent_roots = [
        project_root / ".agents" / "devark",
        repo_root / ".agents" / "devark",
    ]
    for agent_root in agent_roots:
        candidate = agent_root / current_branch
        if candidate.exists():
            plan_base = candidate
            break
    if plan_base is None:
        for agent_root in agent_roots:
            if agent_root.exists():
                candidates = sorted(agent_root.glob("*"))
                if candidates:
                    plan_base = candidates[0]
                    break

    if plan_base and (plan_base / "plan.md").exists():
        shutil.copy2(plan_base / "plan.md", outputs_dir / "plan.md")
    if plan_base and (plan_base / "tasks.md").exists():
        shutil.copy2(plan_base / "tasks.md", outputs_dir / "tasks.md")
    doc_names = spec.get("doc_names") or ([spec["doc_name"]] if "doc_name" in spec else [])
    for doc_name in doc_names:
        doc_path = plan_base / "docs" / doc_name if plan_base else None
        if doc_path and doc_path.exists():
            shutil.copy2(doc_path, outputs_dir / doc_name)
    if plan_base:
        docs_dir = plan_base / "docs"
        if docs_dir.exists():
            for doc_path in sorted(docs_dir.glob("*.md")):
                shutil.copy2(doc_path, outputs_dir / doc_path.name)

    for rel_path in spec["artifact_paths"]:
        src = project_root / rel_path
        dst = outputs_dir / f"artifact__{flatten_name(rel_path)}"
        if src.exists():
            shutil.copy2(src, dst)


def grade_run(run_dir: Path) -> None:
    spec = json.loads((run_dir / "fixture_spec.json").read_text())
    repo_root = Path(spec["repo_root"])
    project_root = Path(spec["project_root"])
    outputs_dir = run_dir / "outputs"

    expectations: list[dict] = []

    def expect(text: str, passed: bool, evidence: str) -> None:
        expectations.append({"text": text, "passed": passed, "evidence": evidence})

    branch = run_cmd(["git", "branch", "--show-current"], repo_root).strip()
    expect(
        "Stayed on the current branch",
        branch == spec["expected_branch"],
        f"current branch: {branch}",
    )

    plan_path = outputs_dir / "plan.md"
    tasks_path = outputs_dir / "tasks.md"
    expect("Persisted plan.md", plan_path.exists(), str(plan_path))
    expect("Persisted tasks.md", tasks_path.exists(), str(tasks_path))

    plan_text = plan_path.read_text() if plan_path.exists() else ""
    if spec["plan_contains"]:
        expect(
            "Plan mentions the task-specific work item",
            any(snippet in plan_text for snippet in spec["plan_contains"]),
            ", ".join(spec["plan_contains"]),
        )

    tasks_text = tasks_path.read_text() if tasks_path.exists() else ""
    expect(
        "Task tracker reached done/completed state",
        "Status: done" in tasks_text or "Status: completed" in tasks_text,
        "Status line checked in tasks.md",
    )
    expect(
        "Task tracker progress is fully updated",
        spec["task_progress"] in tasks_text,
        spec["task_progress"],
    )

    doc_names = spec.get("doc_names") or ([spec["doc_name"]] if "doc_name" in spec else [])
    existing_docs = [name for name in doc_names if (outputs_dir / name).exists()]
    if not existing_docs:
        existing_docs = [
            path.name
            for path in outputs_dir.glob("*.md")
            if path.name not in {"plan.md", "tasks.md"}
            and not path.name.startswith("review-round-")
            and not path.name.startswith("review_round_")
        ]
    expect(
        "Task-specific doc was updated",
        bool(existing_docs),
        ", ".join(existing_docs) if existing_docs else ", ".join(doc_names),
    )

    build_path = outputs_dir / "build_result.json"
    build_ok = False
    build_evidence = "missing build_result.json"
    if build_path.exists():
        build_data = json.loads(build_path.read_text())
        build_ok = build_data.get("status") == "ok" and build_data.get("target") == spec["build_target"]
        build_evidence = f"status={build_data.get('status')} target={build_data.get('target')}"
    else:
        build_doc_path = outputs_dir / "build_verification.md"
        if build_doc_path.exists():
            build_doc = build_doc_path.read_text()
            build_doc_lower = build_doc.lower()
            build_ok = spec["build_target"] in build_doc and (
                "result: `pass`" in build_doc_lower
                or "result: pass" in build_doc_lower
                or "result: passed" in build_doc_lower
            )
            build_evidence = f"build_verification.md target={spec['build_target']}"
    expect("Build verification passed with the expected target", build_ok, build_evidence)

    rev_count = int(run_cmd(["git", "rev-list", "--count", "HEAD"], repo_root).strip())
    expect(
        "Created at least one new commit",
        rev_count >= 2,
        f"git rev-list --count HEAD = {rev_count}",
    )

    git_status_path = outputs_dir / "git_status.txt"
    git_status_lines = []
    if git_status_path.exists():
        git_status_lines = [line.strip() for line in git_status_path.read_text().splitlines() if line.strip()]
    remaining_changes = [
        line
        for line in git_status_lines
        if line != "(clean)"
        if not line.endswith(".devark_eval_build.json")
    ]
    expect(
        "Worktree is clean except ephemeral build logs",
        not remaining_changes,
        "; ".join(remaining_changes) if remaining_changes else "clean",
    )

    for item in evaluate_checks(repo_root, spec["build_checks"]):
        expectations.append(item)

    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed

    timing_path = run_dir / "timing.json"
    timing = json.loads(timing_path.read_text()) if timing_path.exists() else {}

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": 0,
            "transcript_chars": 0,
        },
        "timing": {
            "total_duration_seconds": timing.get("total_duration_seconds", 0.0),
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
    }
    write_json(run_dir / "grading.json", grading)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup")
    setup_parser.add_argument("--workspace", required=True)
    setup_parser.add_argument("--iteration", type=int, default=1)

    collect_parser = subparsers.add_parser("collect")
    collect_parser.add_argument("--run-dir", required=True)
    collect_parser.add_argument("--duration-ms", type=int, default=0)
    collect_parser.add_argument("--total-tokens", type=int, default=0)

    grade_parser = subparsers.add_parser("grade")
    grade_parser.add_argument("--run-dir", required=True)

    args = parser.parse_args(argv)

    if args.command == "setup":
        setup_workspace(Path(args.workspace), args.iteration)
        return 0
    if args.command == "collect":
        collect_outputs(Path(args.run_dir), args.duration_ms, args.total_tokens)
        return 0
    if args.command == "grade":
        grade_run(Path(args.run_dir))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
