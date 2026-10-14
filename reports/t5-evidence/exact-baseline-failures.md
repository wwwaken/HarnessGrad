# Exact valid-baseline failures

Extracted verbatim from pytest JUnit failure elements. Full stdout and captured streams remain in baseline logs.

## test_appworld_service_diagnosis.py::test_runner_mounts_dependency_overlay_once

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_appworld_service_diagnosis/test_runner_mounts_dependency_0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x79a3b356ff80>

    def test_runner_mounts_dependency_overlay_once(tmp_path, monkeypatch):
        repo = tmp_path / "harness"
        repo.mkdir()
        (repo / "harness.json").write_text(json.dumps({"entrypoint": "agent.py"}))
        overlay_path = tmp_path / "overlay"
        overlay_path.mkdir()
        overlay = {"path": overlay_path, "python": "3.11", "install": "requirements.txt",
                   "install_sha256": "abc", "provenance": {}}
        monkeypatch.setenv("HG_AGENT_BACKEND", "mock")
        monkeypatch.delenv("HG_AGENT_BASE_URL", raising=False)
        monkeypatch.setattr(runner.container_mod, "image_python", lambda _: "/usr/local/bin/python3")
        monkeypatch.setattr(runner.harness_runtime, "lookup", lambda *a, **kw: overlay)
        monkeypatch.setattr(runner, "_verify", lambda *a, **kw: {"passed": True})
        commands = []
    
        def launch(argv, **kw):
            # Exercise the actual Docker command builder, including nested mounts.
            cmd = container.command(argv, **{k: v for k, v in kw.items() if k != "timeout_s"})
            destinations = [cmd[i + 1].split("dst=", 1)[1].split(",", 1)[0]
                            for i, value in enumerate(cmd) if value == "--mount"]
            commands.append(cmd)
            assert len(destinations) == len(set(destinations)), "Docker rejects duplicate destinations"
            assert destinations.count(str(overlay_path)) == 1
            assert kw["env"]["PYTHONPATH"].split(":")[0] == str(overlay_path)
            (kw["task_dir"] / "trace.jsonl").write_text('{"actor_started": true}\n')
            return subprocess.CompletedProcess(cmd, 0, "", "")
    
        monkeypatch.setattr(runner.container_mod, "run", launch)
        result = runner.run_one(repo, {"task_id": "train_1"},
                                env={"kind": "exec", "image": "sha256:" + "a" * 64})
>       assert commands and result["exit_code"] == 0
E       assert ([])

tests/quality/test_appworld_service_diagnosis.py:74: AssertionError
```

## test_container.py::test_a_working_harness_scores_full_marks

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_working_harness_scores_0')

    def test_a_working_harness_scores_full_marks(tmp_path):
        """All four tasks, in containers, including `e02`, which is the one that can tell
        a real `exec` run from a `files` run wearing a container's name."""
        _require_docker()
        proc = _run(tmp_path, mode="solve")
>       assert proc.returncode == 0, proc.stdout[-1500:] + proc.stderr[-1500:]
E       AssertionError:   ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity
E           · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026
E         probe
E         
E           harness   probe-exec 1
E           mode      unified · method drives its own loop
E           data      verify_exec · 2 tasks on the train side · train 2 / eval 2
E           model     (none) · mock   ← not a live model
E           sandbox   exec — sha256:9792dc939cfe33d9a9a
E         
E           ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E           ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E           ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.
E         
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_working_harness_scores_0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_working_harness_scores_0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_working_harness_scores_0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode

tests/quality/test_container.py:262: AssertionError
```

## test_container.py::test_an_idle_harness_scores_zero

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_an_idle_harness_scores_ze0')

    def test_an_idle_harness_scores_zero(tmp_path):
        _require_docker()
        proc = _run(tmp_path, mode="idle")
>       assert proc.returncode == 0, proc.stdout[-1500:]
E       AssertionError:   ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity
E           · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026
E         probe
E         
E           harness   probe-exec 1
E           mode      unified · method drives its own loop
E           data      verify_exec · 2 tasks on the train side · train 2 / eval 2
E           model     (none) · mock   ← not a live model
E           sandbox   exec — sha256:9792dc939cfe33d9a9a
E         
E           ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E           ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E         
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_an_idle_harness_scores_ze0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_an_idle_harness_scores_ze0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_an_idle_harness_scores_ze0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode

tests/quality/test_container.py:270: AssertionError
```

## test_container.py::test_a_harness_cannot_grade_itself_in_a_container

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_harness_cannot_grade_it0')

    def test_a_harness_cannot_grade_itself_in_a_container(tmp_path):
        """`e03`, with a harness that rewrites the specification to `sys.exit(0)`.
    
        The same control `verify_demo` runs for the host path, repeated for the container
        path because §2.5.6's guarantee has to hold in both -- and in the container it is
        harder to see, since the harness and the check share a bind mount and the check is
        started by a second `docker run` that the first one has no handle on.
        """
        _require_docker()
        proc = _run(tmp_path, mode="cheat")
>       assert proc.returncode == 0, proc.stdout[-1500:]
E       AssertionError:   ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity
E           · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026
E         probe
E         
E           harness   probe-exec 1
E           mode      unified · method drives its own loop
E           data      verify_exec · 2 tasks on the train side · train 2 / eval 2
E           model     (none) · mock   ← not a live model
E           sandbox   exec — sha256:9792dc939cfe33d9a9a
E         
E           ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E           ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E         
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_harness_cannot_grade_it0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_harness_cannot_grade_it0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_a_harness_cannot_grade_it0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode

tests/quality/test_container.py:320: AssertionError
```

## test_container.py::test_the_curve_records_the_environment

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0')

    def test_the_curve_records_the_environment(tmp_path):
        """§2.5.4. A `files` curve and an `exec` curve are different quantities, and so are
        two `exec` curves under different digests -- so the environment travels with the
        number on every point, not only in `run_meta.json`."""
        _require_docker()
>       assert _run(tmp_path, mode="idle").returncode == 0
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode
E        +    where CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n") = _run(PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_curve_records_the_env0'), mode='idle')

tests/quality/test_container.py:375: AssertionError
```

## test_container.py::test_the_run_record_and_the_curve_agree_about_the_image

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0')

    def test_the_run_record_and_the_curve_agree_about_the_image(tmp_path):
        """The bug this pins, because it is a shape that will be attempted again.
    
        Images were first pinned next to the `env_kinds` gate -- which is where the check
        *logically* belongs, and which runs *after* the header and `run_meta.json` are
        written. So the header named the image's tag, `run_meta.json` recorded
        `image_digest: null`, and every curve point carried the digest. Two records of one
        run disagreeing about what it ran in is precisely the failure §2.5.4 exists to
        prevent, and it was invisible from the curve alone.
        """
        _require_docker()
>       assert _run(tmp_path, mode="idle").returncode == 0
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode
E        +    where CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n") = _run(PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_the_run_record_and_the_cu0'), mode='idle')

tests/quality/test_container.py:507: AssertionError
```

## test_container.py::test_no_sandbox_does_not_disable_the_container

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_no_sandbox_does_not_disab0')

    def test_no_sandbox_does_not_disable_the_container(tmp_path):
        """`--no-sandbox` and the container boundary are different switches.
    
        The container is not a wrapper around the task, it **is** the task's environment
        (INTERFACE.md §2.5.5), so `--no-sandbox` cannot switch it off -- removing it would
        not make the task run unisolated, it would make the task not run at all. What
        `--no-sandbox` does turn off is the host-side bwrap, which for an `exec` dataset is
        already not the boundary. The header has to say so, or a reader sees "no sandbox"
        and concludes there was no boundary anywhere.
        """
        _require_docker()
        proc = _run(tmp_path, mode="solve", extra_argv=("--no-sandbox",))
>       assert proc.returncode == 0, (proc.stdout + proc.stderr)[-1500:]
E       AssertionError:   ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity
E           · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026
E           ! running with --no-sandbox: the harness can read the platform and .env, and only the hash check stands between it and the scorer
E         probe
E         
E           harness   probe-exec 1
E           mode      unified · method drives its own loop
E           data      verify_exec · 2 tasks on the train side · train 2 / eval 2
E           model     (none) · mock   ← not a live model
E           sandbox   exec — sha256:9792dc939cfe33d9a9a (host-side bwrap OFF for the method)
E         
E           ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E           ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable
E           ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.
E         
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_no_sandbox_does_not_disab0/probe_exec_harness', '--mode', 'A', '--rounds', '1', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--no-sandbox', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_no_sandbox_does_not_disab0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container/test_no_sandbox_does_not_disab0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\n  ! running with --no-sandbox: the harness can read the platform and .env, and only the hash check stands between it and the scorer\nprobe\n\n  harness   probe-exec 1\n  mode      unified · method drives its own loop\n  data      verify_exec · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a (host-side bwrap OFF for the method)\n\n  ! e01: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n  ! e02: invalid for dataset 'verify_exec' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_exec' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode

tests/quality/test_container.py:529: AssertionError
```

## test_container_state.py::test_the_oracle_control_passes

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_container_state/test_the_oracle_control_passes0')

    def test_the_oracle_control_passes(tmp_path):
        """**The control that makes every other number on this dataset mean something.**
    
        `base_harness/oracle` runs the dataset's own reference solution and does nothing
        else. If it does not score, the dataset's check is not reachable and no harness's
        score on it means anything -- which is exactly the ambiguity this removes. It found
        three real bugs here: a `docker cp` path that landed the task one directory too deep,
        a `mkdir` issued to a container that was not running yet, and a verifier with no
        network while all 89 real checks install their own test dependencies at verify time.
        """
        from eval.run.runner import run_one
    
        task, setup, verifier, env = _one_ready_task()
        tid = task["task_id"]
        import importlib
        tb = importlib.import_module("data.terminal_bench")
        if not (TB_ROOT / tid / "solution").is_dir():
            pytest.skip(f"{tid} ships no solution for the oracle")
    
        # The oracle is handed the solution through the ordinary SETUP path, which is what
        # the adapter does under HG_TB_ORACLE=1.
        old = os.environ.copy()
        os.environ.update({"HG_TB_ORACLE": "1", "HG_TB_TASKS": tid,
                           "HG_AGENT_BACKEND": "mock",
                           "HARNESSGRAD_WORK_ROOT": str(tmp_path / "work")})
        try:
            resolved, problem = __import__("driver")._resolve_envs({tid: env})
            assert problem is None, problem
            setup = {"files": [{"path": ".oracle",
                                "from": str(TB_ROOT / tid / "solution")}]}
            result = run_one((ROOT / "base_harness" / "oracle"), task, sandbox=True,
                             setup=setup, verifier=verifier, env=resolved[tid],
                             # Per process, for the same reason as the leak test below: a
                             # fixed id means an interrupted run leaves a network named
                             # `hg-oracle-test-<task>` behind, and from then on this test fails
                             # with `network ... already exists` -- red for a reason that has
                             # nothing to do with the oracle. Measured 2026-10-06, on an
                             # unmodified checkout: both this test and the leak test below were
                             # failing that way, so nothing but a manual `docker network rm`
                             # could make them green again.
                             run_id=f"oracle-test-{os.getpid()}", run_seed="s",
                             recordings_root=tmp_path / "recordings")
        finally:
            os.environ.clear()
            os.environ.update(old)
    
        verdict = result.get("verdict") or {}
        # A check that could not fetch its *own* tooling says nothing about whether the
        # platform can reach it, so it is skipped loudly rather than counted as a failure.
        # Anything else **fails**: that is the whole job of this control.
        why = _environmental(verdict)
        if why is not None:
            pytest.skip(
                f"the host could not fetch the check's own tooling ({why!r}), so this run "
                f"measured the network and not the platform. The oracle is verified "
                f"conditionally, not permanently.")
>       assert verdict.get("score") == 1.0, (
            f"the oracle did not pass {tid}, so its check is not reachable and no harness's "
            f"score on this dataset means anything yet: "
            f"{json.dumps(verdict, ensure_ascii=False)[:800]}")
E       AssertionError: the oracle did not pass cancel-async-tasks, so its check is not reachable and no harness's score on this dataset means anything yet: {}
E       assert None == 1.0
E        +  where None = <built-in method get of dict object at 0x7bd7d8f2f200>('score')
E        +    where <built-in method get of dict object at 0x7bd7d8f2f200> = {}.get

tests/quality/test_container_state.py:405: AssertionError
```

## test_jericho_runtime_admission.py::test_live_backend_is_refused_before_staging_or_execution

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_jericho_runtime_admission/test_live_backend_is_refused_b0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x76935d198170>

    def test_live_backend_is_refused_before_staging_or_execution(tmp_path, monkeypatch):
        repo = tmp_path / "harness"
        repo.mkdir()
        (repo / "harness.json").write_text(json.dumps({"entrypoint": "agent.py"}))
        monkeypatch.setenv("HG_AGENT_BACKEND", "openai")
    
        def unexpected(*args, **kwargs):
            pytest.fail("admission must happen before allocating task storage")
    
        monkeypatch.setattr("eval.run.runner.tempfile.mkdtemp", unexpected)
>       with pytest.raises(ValueError, match="live agent backend"):
E       Failed: DID NOT RAISE <class 'ValueError'>

tests/quality/test_jericho_runtime_admission.py:52: Failed
```

## test_jericho_runtime_boundaries.py::test_runner_refuses_unsandboxed_declared_isolation

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_jericho_runtime_boundaries/test_runner_refuses_unsandboxe0')

    def test_runner_refuses_unsandboxed_declared_isolation(tmp_path):
        repo = harness(tmp_path / "harness", "raise AssertionError('must not execute')")
>       with pytest.raises(ValueError, match="requires sandbox"):
E       Failed: DID NOT RAISE <class 'ValueError'>

tests/quality/test_jericho_runtime_boundaries.py:149: Failed
```

## test_jericho_runtime_boundaries.py::test_agent_projection_network_denial_and_trusted_verifier_end_to_end

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_jericho_runtime_boundaries/test_agent_projection_network_0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7d554c89ac60>

    @pytest.mark.skipif(shutil.which("bwrap") is None, reason="bubblewrap unavailable")
    def test_agent_projection_network_denial_and_trusted_verifier_end_to_end(tmp_path, monkeypatch):
        # A separate synthetic platform tree preserves the production staging rule.
        # All test writes remain in the user-authorized worktree.
        platform = tmp_path / "platform"
        platform.mkdir()
        monkeypatch.setattr("eval.run.runner.PLATFORM_ROOT", platform)
        monkeypatch.setattr("eval.verification.verifier.PLATFORM_ROOT", platform)
        work = tmp_path / "work"
        package = work / "packages" / "boundary_fixture"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text('REFERENCE = "SYNTHETIC_SECRET"\n')
        (package / "game_info.py").write_text('REFERENCE = "SYNTHETIC_SECRET"\n')
        (package / "__pycache__").mkdir()
        (package / "__pycache__/game_info.pyc").write_bytes(b"SYNTHETIC_SECRET")
        runtime = {"package_dir": str(package), "files": [{"path": "__init__.py", "content": "PUBLIC = True\n"}]}
        monkeypatch.setenv("HG_AGENT_BACKEND", "mock")
        monkeypatch.setenv("HARNESSGRAD_WORK_ROOT", str(work))
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            host_port = listener.getsockname()[1]
            body = f'''import argparse, json, os, pathlib, socket, sys
    ap = argparse.ArgumentParser(); ap.add_argument('--task'); ap.add_argument('--workdir'); a = ap.parse_args()
    assert os.environ['HG_AGENT_DEADLINE_S'] == '3'
    sys.path.insert(0, {str(package.parent)!r})
    import boundary_fixture as pkg
    seen = {{'public': pkg.PUBLIC, 'reference': hasattr(pkg, 'REFERENCE'),
            'data': pathlib.Path(pkg.__file__).with_name('game_info.py').exists(),
            'bytecode': pathlib.Path(pkg.__file__).with_name('__pycache__').exists()}}
    try:
        pathlib.Path(pkg.__file__).write_text('rewritten'); seen['writable'] = True
    except OSError:
        seen['writable'] = False
    for label, target in [('egress', ('192.0.2.1', 9)), ('host_loopback', ('127.0.0.1', {host_port}))]:
        with socket.socket() as sock:
            sock.settimeout(.2)
            try:
                sock.connect(target); seen[label] = True
            except OSError:
                seen[label] = False
    pathlib.Path(a.workdir, 'answer.txt').write_text(json.dumps(seen))
    '''
            repo = harness(work / "run/workspace", body)
            verifier = {"kind": "command", "timeout_s": 2, "argv": [sys.executable, "-c",
                f"import sys; sys.path.insert(0, {str(package.parent)!r}); import boundary_fixture as p; "
                "assert p.REFERENCE == 'SYNTHETIC_SECRET'; print('trusted package retained')"]}
            result = run_one(repo, {"task_id": "synthetic", "goal": "synthetic"},
                             env={"kind": "files", "network": "none", "agent_timeout_s": 3,
                                  "verify_timeout_s": 5, "agent_runtime": runtime}, verifier=verifier)
>       assert result["exit_code"] == 0, result["stderr"]
E       AssertionError: 
E       assert None == 0

tests/quality/test_jericho_runtime_boundaries.py:204: AssertionError
```

## test_services.py::test_a_service_that_is_not_healthy_refuses_the_task

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_service_that_is_not_hea0')

    def test_a_service_that_is_not_healthy_refuses_the_task(tmp_path):
        """**The negative control for the whole invalid category.**
    
        A service that is listening but whose own health check never passes must produce an
        `invalid` task -- attributed to the dataset and the service -- and not a zero. A
        zero here is indistinguishable from a weak harness, which is the distinction this
        platform exists to preserve.
        """
        _require_docker()
        spec = _env([_service(health={"argv": ["false"], "timeout_s": 3})])
        result = _evaluate(tmp_path, spec)
        # Nothing was scored, so the caller has to be able to see that it was not.
        assert "s01" not in result["per_task"], (
            f"an unmeasurable task was given a score: {result['per_task']}")
>       assert result["invalid"]["s01"]["stage"] == "health"
E       AssertionError: assert 'admission' == 'health'
E         - health
E         + admission

tests/quality/test_services.py:344: AssertionError
```

## test_services.py::test_the_same_task_scores_when_its_service_is_healthy

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_same_task_scores_when0')

    def test_the_same_task_scores_when_its_service_is_healthy(tmp_path):
        """The other half: the test above is only a measurement if the healthy case passes.
    
        Same task, same harness, same everything except the health command -- so the
        difference in outcome is the health check and nothing else.
        """
        _require_docker()
        result = _evaluate(tmp_path, _env(), verifier={
            "kind": "command", "argv": [
                "python3", "-c",
                "import json,pathlib,sys;"
                "p=pathlib.Path('/recordings/orders/harnessgrad.json');"
                "d=json.loads(p.read_text()) if p.exists() else {};"
                "sys.exit(0 if any(r.get('path')=='/orders' for r in d.get('received',[])) else 1)"]})
>       assert result["invalid"] == {}, result["invalid"]
E       AssertionError: {'s01': {'detail': 'backend_observation_unavailable', 'receipt': {'measured': False, 'observation': 'unknown', 'policy...s': ['env.exec_defaults', 'env.network'], 'production_authorized': False, ...}, 'service': None, 'stage': 'admission'}}
E       assert {'s01': {'stage': 'admission', 'service': None, 'detail': 'backend_observation_unavailable', 'receipt': {'schema': 'harnessgrad.runner-policy-refusal.v1', 'stage': 'admission', 'status': 'blocked', 'reason': 'backend_observation_unavailable', 'measured': False, 'production_authorized': False, 'observation': 'unknown', 'policy_fields': ['env.exec_defaults', 'env.network']}}} == {}
E         Left contains 1 more item:
E         {'s01': {'detail': 'backend_observation_unavailable',
E                  'receipt': {'measured': False,
E                              'observation': 'unknown',
E                              'policy_fields': ['env.exec_defaults', 'env.network'],
E                              'production_authorized': False,
E                              'reason': 'backend_observation_unavailable',
E                              'schema': 'harnessgrad.runner-policy-refusal.v1',
E                              'stage': 'admission',
E                              'status': 'blocked'},
E                  'service': None,
E                  'stage': 'admission'}}
E         Full diff:
E           {
E         -  ,
E         +  's01': {'detail': 'backend_observation_unavailable',
E         +          'receipt': {'measured': False,
E         +                      'observation': 'unknown',
E         +                      'policy_fields': ['env.exec_defaults',
E         +                                        'env.network'],
E         +                      'production_authorized': False,
E         +                      'reason': 'backend_observation_unavailable',
E         +                      'schema': 'harnessgrad.runner-policy-refusal.v1',
E         +                      'stage': 'admission',
E         +                      'status': 'blocked'},
E         +          'service': None,
E         +          'stage': 'admission'},
E           }

tests/quality/test_services.py:363: AssertionError
```

## test_services.py::test_reap_removes_a_service_container_a_crash_left_running

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_reap_removes_a_service_co0')

    def test_reap_removes_a_service_container_a_crash_left_running(tmp_path):
        """`docker run --rm` 只在容器**退出**时删它,而被杀掉的 driver 从不 stop 它。
    
        实测:一个 probe 跑道的服务容器在宿主上挂了 15 小时。清容器必须在清网络**之前** ——
        网络上有容器时 `docker network rm` 会失败。
        """
        _require_docker()
        run_id = "reaped-crash"
>       running = services.start([_service()], recordings_root=tmp_path / "rec",
                                 run_id=run_id, task_id="s01", run_seed="R")

tests/quality/test_services.py:456: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

services = [{'health': {'argv': ['python3', '-c', "import urllib.request as u;u.urlopen('http://localhost:8080/health', timeout=2...sha256:3a3d25e5d25065b2599076f8de628eb473dbcfdebe3014c0814ed71196b33c18', 'name': 'orders', 'needs_model': False, ...}]

    def start(services: list[dict], *, recordings_root: Path, run_id: str,
              task_id: str, run_seed: str) -> RunningServices:
        """Create the network, start every service, and wait for each to be healthy.
    
        Raises `ServiceUnavailable` — having already torn down whatever it started, so a
        failed task does not leave a network behind for the next one to inherit.
        """
        # The same safety net `eval/container.run` carries, for the same reason: the driver
        # pins every service image before the run starts (§2.5.4), and a service started
        # from a tag would pull whatever the registry served that day.
        for svc in services:
            if not container_mod.looks_pinned(svc["image"]):
                raise ServiceUnavailable(
                    f"service {svc['name']!r} names {svc['image']!r}, which is not pinned "
                    f"to a content address. Resolve it with `container.resolve_digest` "
                    f"first (INTERFACE.md §2.5.4).", service=svc["name"], stage="start")
    
>       net = create_network(run_id, task_id)

eval/service/services.py:361: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

run_id = 'reaped-crash', task_id = 's01'

    def create_network(run_id: str, task_id: str) -> str:
        """Create the task's `--internal` network. Returns its name.
    
        Public because a task needs one even when it declares no services: a containerised
        harness cannot reach a model on the host's loopback, so the platform publishes the
        endpoint on this network (`eval/service/modelgate.py`). Without that the harness has no
        model, and a harness with no model is not being measured.
        """
        net = label(f"hg-{run_id}-{task_id}")
        proc = container_mod.docker("network", "create", "--internal", net,
                                    "--label", f"harnessgrad.run={run_id}",
                                    "--label", f"harnessgrad.task={task_id}", timeout=120)
        if proc.returncode != 0:
>           raise ServiceUnavailable(
                f"could not create the internal network for task {task_id!r}: "
                f"{proc.stderr.strip()[:300]}")
E           eval.service.services.ServiceUnavailable: could not create the internal network for task 's01': Error response from daemon: network with name hg-reaped-crash-s01 already exists

eval/service/services.py:254: ServiceUnavailable
```

## test_services.py::test_a_healthy_service_run_names_the_service_in_its_header

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_healthy_service_run_nam0')

    def test_a_healthy_service_run_names_the_service_in_its_header(tmp_path):
        """The header is where a reader takes the run's conditions from, and "a mock API
        was reachable" is a condition."""
        _require_docker()
        proc = _run_driver(tmp_path, "verify_service", extra_env={"HG_AGENT_PROBE": "idle"})
>       assert proc.returncode == 0, _said(proc)[-1500:]
E       AssertionError: ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026 probe harness svc-probe 1 mode unified · method drives its own loop data verify_service · 2 tasks on the train side · train 2 / eval 2 model (none) · mock ← not a live model sandbox exec — sha256:9792dc939cfe33d9a9a + services[orders] ! s01: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable ! s02: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable ✗ refusing to run: none of the 2 tasks in 'verify_service' produced a scoreable result. The curve would have to report a score for a task set that was never measured.
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_healthy_service_run_nam0/svc_harness', '--mode', 'A', '--rounds', '0', '--sampling', 'all', '--dataset', 'verify_service', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_healthy_service_run_nam0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_healthy_service_run_nam0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   svc-probe 1\n  mode      unified · method drives its own loop\n  data      verify_service · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a + services[orders]\n\n  ! s01: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable\n  ! s02: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_service' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode

tests/quality/test_services.py:652: AssertionError
```

## test_services.py::test_the_declared_environment_reaches_the_curve

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0')

    def test_the_declared_environment_reaches_the_curve(tmp_path):
        _require_docker()
>       assert _run_driver(tmp_path, "verify_service",
                           extra_env={"HG_AGENT_PROBE": "idle"}).returncode == 0
E       assert 2 == 0
E        +  where 2 = CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0/svc_harness', '--mode', 'A', '--rounds', '0', '--sampling', 'all', '--dataset', 'verify_service', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   svc-probe 1\n  mode      unified · method drives its own loop\n  data      verify_service · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a + services[orders]\n\n  ! s01: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable\n  ! s02: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_service' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n").returncode
E        +    where CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0/svc_harness', '--mode', 'A', '--rounds', '0', '--sampling', 'all', '--dataset', 'verify_service', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout="  ! no improver resolved (the 'deepseek' improver needs DEEPSEEK_API_KEY); a method that carries its own improver still runs, but this run carries no improver identity\n  · container boundary holds (docker 29.2.1): image sha256:9792dc939cfe33d9a9a30138a7f178420bd626afcefa779c4408f52cc8a02750: docker_socket=no, harness_readable=yes, harness_writable=no, platform_visible=no, rootfs_writable=no, sibling_visible=no, state_writable=yes, task_writable=yes, tmp_writable=yes, uid=1026\nprobe\n\n  harness   svc-probe 1\n  mode      unified · method drives its own loop\n  data      verify_service · 2 tasks on the train side · train 2 / eval 2\n  model     (none) · mock   ← not a live model\n  sandbox   exec — sha256:9792dc939cfe33d9a9a + services[orders]\n\n  ! s01: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable\n  ! s02: invalid for dataset 'verify_service' at stage 'admission' -- backend_observation_unavailable\n", stderr="  ✗ refusing to run: none of the 2 tasks in 'verify_service' produced a scoreable result. The curve would have to report a score for a task set that was never measured.\n") = _run_driver(PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_the_declared_environment_0'), 'verify_service', extra_env={'HG_AGENT_PROBE': 'idle'})

tests/quality/test_services.py:658: AssertionError
```

## test_services.py::test_a_containerised_harness_gets_its_model_and_not_the_internet

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_containerised_harness_g0')

    def test_a_containerised_harness_gets_its_model_and_not_the_internet(tmp_path):
        """The end-to-end version, through `run_one`: the run records `model_gateway`, the
        harness's base URL was rewritten to the published address, and the internet is still
        unreachable from inside."""
        _require_docker()
        import http.server
        import threading
        from eval.service import modelgate
    
        # A stand-in model on the host's loopback, which is what the container cannot reach
        # directly -- so passing this test cannot be an accident of the host being reachable.
        class _H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):                           # noqa: N802
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
    
            def log_message(self, *a):
                pass
    
        loopback = http.server.HTTPServer(("127.0.0.1", 0), _H)
        port = loopback.server_address[1]
        threading.Thread(target=loopback.serve_forever, daemon=True).start()
    
        harness = tmp_path / "gl_harness"
        harness.mkdir()
        (harness / "harness.json").write_text(json.dumps({
            "name": "gl", "version": "1", "entrypoint": "agent.py", "backend": "cli",
            "env_kinds": ["exec"]}))
        (harness / "agent.py").write_text(
            "import argparse, json, os, pathlib, urllib.request\n"
            "ap = argparse.ArgumentParser()\n"
            "ap.add_argument('--task'); ap.add_argument('--workdir')\n"
            "a = ap.parse_args()\n"
            "w = pathlib.Path(a.workdir)\n"
            "base = os.environ['HG_AGENT_BASE_URL']\n"
            "seen = urllib.request.urlopen(base, timeout=10).read().decode()\n"
            "try:\n"
            "    urllib.request.urlopen('http://1.1.1.1', timeout=4)\n"
            "    net = 'internet'\n"
            "except Exception:\n"
            "    net = 'offline'\n"
            "(w / 'answer.txt').write_text(f'{base}|{seen}|{net}')\n"
            "(w / 'trace.jsonl').write_text('{}\\n')\n")
    
        old = os.environ.copy()
        os.environ.update({"HG_AGENT_BACKEND": "openai",
                           "HG_AGENT_BASE_URL": f"http://127.0.0.1:{port}",
                           "HARNESSGRAD_WORK_ROOT": str(tmp_path / "work")})
        try:
            result = run_one(
                harness, {"task_id": "g01", "goal": "call the model"}, sandbox=True,
                env={"kind": "exec", "image": _pin(DEMO_IMAGE), "workdir": "/app",
                     "network": "none", "placement": "inside", "services": []},
                run_id="gl", run_seed="s", recordings_root=tmp_path / "rec")
        finally:
            loopback.shutdown()
            loopback.server_close()
            os.environ.clear()
            os.environ.update(old)
    
>       assert result["answer"].startswith("http://"), result["answer"]
E       AssertionError: 
E       assert False
E        +  where False = <built-in method startswith of str object at 0x956e70>('http://')
E        +    where <built-in method startswith of str object at 0x956e70> = ''.startswith

tests/quality/test_services.py:818: AssertionError
```

## test_services.py::test_a_remote_model_with_an_offline_network_is_refused

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_remote_model_with_an_of0')

    def test_a_remote_model_with_an_offline_network_is_refused(tmp_path):
        """A containerised harness whose model is not on this host needs the internet, and a
        task that did not ask for the internet must not silently get it. Refused rather than
        attempted: the harness would have no model, so every score would be a zero that
        means nothing and would look like a weak harness."""
        _require_docker()
        proc = _run_driver(tmp_path, "verify_exec",
                           extra_env={"HG_AGENT_BACKEND": "openai",
                                      "HG_AGENT_BASE_URL": "https://api.example.com/v1",
                                      "HG_AGENT_API_KEY": "x"})
        assert proc.returncode == 2, _said(proc)[-1500:]
>       assert "not on this host" in _said(proc), _said(proc)[-1200:]
E       AssertionError: backend is 'openai' but HG_AGENT_MODEL is unset; every score would come from a harness that cannot reach a model. See .env.example.
E       assert 'not on this host' in "backend is 'openai' but HG_AGENT_MODEL is unset; every score would come from a harness that cannot reach a model. See .env.example."
E        +  where "backend is 'openai' but HG_AGENT_MODEL is unset; every score would come from a harness that cannot reach a model. See .env.example." = _said(CompletedProcess(args=['/mnt/8t/xubuqiang/anaconda3/bin/python', 'driver.py', '--harness', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_remote_model_with_an_of0/svc_harness', '--mode', 'A', '--rounds', '0', '--sampling', 'all', '--dataset', 'verify_exec', '--run-id', 'probe', '--runs-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_remote_model_with_an_of0/runs', '--work-root', '/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_services/test_a_remote_model_with_an_of0/work', '--method-entrypoint', '/mnt/8t/xubuqiang/anaconda3/bin/python /tmp/hg-t5/methods/noop/run.py'], returncode=2, stdout='', stderr="backend is 'openai' but HG_AGENT_MODEL is unset; every score would come from a harness that cannot reach a model. See .env.example.\n"))

tests/quality/test_services.py:846: AssertionError
```

## test_web_gateway.py::test_declared_task_gets_web_url_and_undeclared_task_cannot_reach_live_gateway

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_web_gateway/test_declared_task_gets_web_ur0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7710828c2c90>

    def test_declared_task_gets_web_url_and_undeclared_task_cannot_reach_live_gateway(tmp_path, monkeypatch):
        """A negative connection probe against a confirmed live, named destination."""
        if container.available() is None:
            pytest.skip("no docker daemon")
        try:
            image = container.resolve_digest(DEMO_IMAGE)
        except container.ContainerUnavailable:
            pytest.skip("demo exec image is not available")
        monkeypatch.setenv("HG_WEB_SEARCH", "none")
        monkeypatch.setenv("HG_WEB_FETCH", "http")
        repo = tmp_path / "harness"
        repo.mkdir()
        (repo / "harness.json").write_text(json.dumps({
            "name": "web-probe", "version": "1", "entrypoint": "agent.py",
            "env_kinds": ["exec"]}))
        (repo / "agent.py").write_text("""
    import argparse, json, os, pathlib, urllib.request, urllib.error
    p=argparse.ArgumentParser(); p.add_argument('--task'); p.add_argument('--workdir'); a=p.parse_args()
    w=pathlib.Path(a.workdir); base=os.environ.get('HG_SVC_WEB_URL')
    probe=json.loads((w/'task.json').read_text())['probe_url']
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    if base:
        req=urllib.request.Request(base+'/search', data=b'{"query":"x","num":1}', method='POST')
        result=json.loads(opener.open(req, timeout=5).read())
        answer='searchable' if result == {'results': []} else 'bad'
    else:
        req=urllib.request.Request(probe+'/search', data=b'{"query":"x","num":1}', method='POST')
        try:
            opener.open(req, timeout=2).read()
            answer='reachable'
        except urllib.error.HTTPError:
            answer='reachable-http-error'
        except urllib.error.URLError:
            answer='absent-and-blocked'
    (w/'answer.txt').write_text(answer); (w/'trace.jsonl').write_text('{}\\n')
    """)
        common = {"kind": "exec", "image": image, "workdir": "/app",
                  "placement": "inside", "services": []}
        network = services.create_network("web-isolation", "live-probe")
        try:
            probe = WebGateway(bind_host=services.gateway_ip(network)).start()
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                # The host confirms liveness before and after the isolated container probe.
                assert json.loads(opener.open(probe.url + '/health').read())["ok"]
                with_web = run_one(repo, {"task_id": "with", "goal": "web", "probe_url": probe.url},
                                   sandbox=True,
                                   env={**common, "network": "services", "web": {"search": True, "fetch": True}},
                                   run_id="web-cap", run_seed="s", recordings_root=tmp_path / "recordings")
                without_web = run_one(repo, {"task_id": "without", "goal": "offline", "probe_url": probe.url},
                                      sandbox=True, env={**common, "network": "none"}, run_id="web-cap",
                                      run_seed="s", recordings_root=tmp_path / "recordings")
                assert json.loads(opener.open(probe.url + '/health').read())["ok"]
            finally:
                probe.stop()
        finally:
            assert services.remove_network(network) in (None, [])
>       assert with_web["exit_code"] == without_web["exit_code"] == 0, (with_web, without_web)
E       AssertionError: ({'answer': '', 'env_usage': {}, 'exit_code': None, 'identity': None, ...}, {'answer': '', 'env_usage': {}, 'exit_code': None, 'identity': None, ...})
E       assert None == 0

tests/quality/test_web_gateway.py:220: AssertionError
```

## test_web_gateway.py::test_driver_writes_real_run_meta_before_task_launch[searxng-http://127.0.0.1:19999]

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_web_gateway/test_driver_writes_real_run_me0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x771081704dd0>
provider = 'searxng', endpoint = 'http://127.0.0.1:19999'

    @pytest.mark.parametrize('provider,endpoint', [('searxng', 'http://127.0.0.1:19999'), ('none', None)])
    def test_driver_writes_real_run_meta_before_task_launch(tmp_path, monkeypatch, provider, endpoint):
        import driver
        from harnessgrad import config
        config.reset()
        monkeypatch.setenv('HG_AGENT_BACKEND', 'mock')
        monkeypatch.setenv('HG_AGENT_MODEL', 'dummy')
        monkeypatch.setenv('HG_WEB_SEARCH', provider)
        monkeypatch.setenv('HG_WEB_FETCH', 'http')
        monkeypatch.setenv('HG_WEB_SEARXNG_URL', endpoint or 'http://unused.test')
        monkeypatch.setattr(driver, 'load_env', lambda *_args: {})
        task = {'task_id': 'fixture', 'goal': 'probe'}
        env = {'fixture': {'kind': 'exec', 'image': 'fixture', 'network': 'services',
                           'web': {'search': True, 'fetch': True}}}
        monkeypatch.setattr(driver.datasets, 'load_split', lambda *_args: ([task], {}, None))
        monkeypatch.setattr(driver.datasets, 'load_tasks', lambda *_args: ([task], {}, {}))
        monkeypatch.setattr(driver.datasets, 'load_envs', lambda *_args: env)
        monkeypatch.setattr(driver.datasets, 'oracle_source', lambda *_args: ('released', 'fixture'))
        monkeypatch.setattr(driver, '_resolve_envs', lambda specs: (specs, None))
        monkeypatch.setattr(driver.container, 'available', lambda: 'fixture')
        monkeypatch.setattr(driver.container, 'self_check', lambda *_args: {'ok': True, 'detail': 'fixture'})
        monkeypatch.setattr(driver, '_warn_missing_overlay', lambda *_args: None)
        monkeypatch.setattr(driver.services_mod, 'reap', lambda *_args: [])
        class BeforeTaskLaunch(Exception):
            pass
        def inspect_meta(*args):
            meta = json.loads((tmp_path / 'runs/meta/run_meta.json').read_text())
            assert meta['web_search_provider'] == provider
            assert meta['web_fetch_provider'] == 'http'
            assert meta.get('web_searxng_url') == endpoint
            assert meta['env']['web']['search_provider'] == provider
            raise BeforeTaskLaunch()
        monkeypatch.setattr(driver, 'stage_workspace', inspect_meta)
        monkeypatch.setattr(sys, 'argv', ['driver.py', '--harness', 'oracle', '--dataset', 'demo',
            '--rounds', '0', '--improver', 'none', '--no-sandbox', '--run-id', 'meta',
            '--runs-root', str(tmp_path / 'runs'), '--work-root', str(tmp_path / 'work')])
        try:
>           with pytest.raises(BeforeTaskLaunch):
E           Failed: DID NOT RAISE <class 'test_web_gateway.test_driver_writes_real_run_meta_before_task_launch.<locals>.BeforeTaskLaunch'>

tests/quality/test_web_gateway.py:437: Failed
```

## test_web_gateway.py::test_driver_writes_real_run_meta_before_task_launch[none-None]

```text
tmp_path = PosixPath('/mnt/20t/xubuqiang/.hg-pytest/t5/baseline-test_web_gateway/test_driver_writes_real_run_me1')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x77108174bfb0>
provider = 'none', endpoint = None

    @pytest.mark.parametrize('provider,endpoint', [('searxng', 'http://127.0.0.1:19999'), ('none', None)])
    def test_driver_writes_real_run_meta_before_task_launch(tmp_path, monkeypatch, provider, endpoint):
        import driver
        from harnessgrad import config
        config.reset()
        monkeypatch.setenv('HG_AGENT_BACKEND', 'mock')
        monkeypatch.setenv('HG_AGENT_MODEL', 'dummy')
        monkeypatch.setenv('HG_WEB_SEARCH', provider)
        monkeypatch.setenv('HG_WEB_FETCH', 'http')
        monkeypatch.setenv('HG_WEB_SEARXNG_URL', endpoint or 'http://unused.test')
        monkeypatch.setattr(driver, 'load_env', lambda *_args: {})
        task = {'task_id': 'fixture', 'goal': 'probe'}
        env = {'fixture': {'kind': 'exec', 'image': 'fixture', 'network': 'services',
                           'web': {'search': True, 'fetch': True}}}
        monkeypatch.setattr(driver.datasets, 'load_split', lambda *_args: ([task], {}, None))
        monkeypatch.setattr(driver.datasets, 'load_tasks', lambda *_args: ([task], {}, {}))
        monkeypatch.setattr(driver.datasets, 'load_envs', lambda *_args: env)
        monkeypatch.setattr(driver.datasets, 'oracle_source', lambda *_args: ('released', 'fixture'))
        monkeypatch.setattr(driver, '_resolve_envs', lambda specs: (specs, None))
        monkeypatch.setattr(driver.container, 'available', lambda: 'fixture')
        monkeypatch.setattr(driver.container, 'self_check', lambda *_args: {'ok': True, 'detail': 'fixture'})
        monkeypatch.setattr(driver, '_warn_missing_overlay', lambda *_args: None)
        monkeypatch.setattr(driver.services_mod, 'reap', lambda *_args: [])
        class BeforeTaskLaunch(Exception):
            pass
        def inspect_meta(*args):
            meta = json.loads((tmp_path / 'runs/meta/run_meta.json').read_text())
            assert meta['web_search_provider'] == provider
            assert meta['web_fetch_provider'] == 'http'
            assert meta.get('web_searxng_url') == endpoint
            assert meta['env']['web']['search_provider'] == provider
            raise BeforeTaskLaunch()
        monkeypatch.setattr(driver, 'stage_workspace', inspect_meta)
        monkeypatch.setattr(sys, 'argv', ['driver.py', '--harness', 'oracle', '--dataset', 'demo',
            '--rounds', '0', '--improver', 'none', '--no-sandbox', '--run-id', 'meta',
            '--runs-root', str(tmp_path / 'runs'), '--work-root', str(tmp_path / 'work')])
        try:
>           with pytest.raises(BeforeTaskLaunch):
E           Failed: DID NOT RAISE <class 'test_web_gateway.test_driver_writes_real_run_meta_before_task_launch.<locals>.BeforeTaskLaunch'>

tests/quality/test_web_gateway.py:437: Failed
```

