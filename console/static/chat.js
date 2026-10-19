/* 对话窗口 · 一个技能：跑实验。
 *
 * 两条刻意的限制：
 *   1. 这里**没有模型**。卡片是确定性表单，把人说的那句话变成一次可确认的运行。
 *   2. 起跑前必须点两次（预览 → 确认启动），并且由服务端判定能不能跑：
 *      有 driver 活着就 409。前端只显示这个判定，不自己拟一个"应该没问题"。
 */
(() => {
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  const store = {
    key: "hg.chat.v1",
    read() { try { return JSON.parse(sessionStorage.getItem(this.key) || "null") || { idx: 0, sessions: [] }; } catch { return { idx: 0, sessions: [] }; } },
    write(v) { sessionStorage.setItem(this.key, JSON.stringify(v)); },
  };

  let state = store.read();
  let form = null;          // 技能卡的当前取值
  let preview = "";         // 服务端生成的等效命令
  let blocked = null;       // 阻塞项
  let launched = null;      // 上一次启动的结果

  function session() {
    if (!state.sessions.length) state.sessions.push({ id: Date.now(), title: "新的运行", msgs: [] });
    return state.sessions[state.idx] || state.sessions[0];
  }
  function persist() { store.write(state); }

  /* ── 拉选择器的取值 ───────────────────────────────── */
  async function loadForm() {
    const r = await fetch("/api/launch/form", { headers: { Accept: "application/json" } });
    const d = await r.json();
    form = { ...d.defaults, improver: (d.improvers[0] || {}).name || "dsh",
             improver_model: (d.improvers[0] || {}).model || "" };
    return d;
  }

  async function refreshPreview() {
    const q = new URLSearchParams({ dataset: form.dataset, harness: form.harness,
      rounds: form.rounds, jobs: form.jobs, trials: form.trials, improver: form.improver,
      improver_model: form.improver_model, sampling: form.sampling });
    const r = await fetch(`/api/launch/preview?${q}`);
    const d = await r.json();
    preview = (d.argv || []).map((a) => (/[\s"]/.test(a) ? JSON.stringify(a) : a)).join(" ");
    const live = await (await fetch("/api/health")).json();
    blocked = (live.running || []).length
      ? `已有 driver 在跑：${live.running.map((x) => x.run_id).join("、")}` : null;
    render();
  }

  /* ── 渲染 ─────────────────────────────────────────── */
  function render() {
    // 会话列表
    $("#sessions").innerHTML = state.sessions.map((s, i) =>
      `<button class="s" data-i="${i}" aria-current="${i === state.idx}">${esc(s.title)}</button>`).join("");
    $("#sessions").querySelectorAll("[data-i]").forEach((b) => {
      b.onclick = () => { state.idx = Number(b.dataset.i); persist(); render(); };
    });

    // 消息流
    const msgs = session().msgs.map((m) => `<div class="msg" data-who="${m.who === "user" ? "user" : "ai"}">
        <div class="avatar">${m.who === "user" ? "你" : "HG"}</div>
        <div class="msg-body"><div class="msg-who">${m.who === "user" ? "你" : "助手"}</div>
        <div class="msg-text"><p>${esc(m.text)}</p></div></div></div>`).join("");

    const card = form ? `<div class="skill2">
      <h4>⚡ 跑实验 <span style="font-weight:400;color:var(--hg-alias-label-secondary)">确定性表单 · 没有模型参与</span></h4>
      <div class="rows2">
        <label for="f-ds">数据集</label>
        <select id="f-ds">${(window.FORM.datasets).map((x) =>
          `<option value="${esc(x.name)}"${x.name === form.dataset ? " selected" : ""}>${esc(x.name)}</option>`).join("")}</select>
        <label for="f-h">基线 harness</label>
        <select id="f-h">${window.FORM.harnesses.map((h) =>
          `<option${h === form.harness ? " selected" : ""}>${esc(h)}</option>`).join("")}</select>
        <label for="f-imp">改进器</label>
        <select id="f-imp">${window.FORM.improvers.map((x) =>
          `<option value="${esc(x.name)}|${esc(x.model)}"${x.name === form.improver ? " selected" : ""}>${esc(x.name)}${x.model ? " + " + esc(x.model) : ""}</option>`).join("")}</select>
        <label for="f-r">轮数</label><input id="f-r" type="number" min="1" max="20" value="${esc(form.rounds)}">
        <label for="f-j">并发</label><input id="f-j" type="number" min="1" max="64" value="${esc(form.jobs)}">
        <label for="f-t">trials</label><input id="f-t" type="number" min="1" max="3" value="${esc(form.trials)}">
      </div>
      <pre class="cmd2">${esc(preview || "（生成等效命令…）")}</pre>
      <div class="foot2">
        <span class="${blocked ? "blocked" : "ok2"}">${esc(blocked || "没有 driver 在跑，可以起跑")}</span>
        <span class="spacer"></span>
        <button class="btn" id="confirm">确认启动</button>
      </div>
      <div class="note2">启动后跑的是平台自己的 driver.py；本页只负责生成命令与提交，不代跑、不改写命令。</div>
      ${launched ? `<div class="note2 ok2">已提交：<code>${esc(launched.run_id)}</code> · 日志 <code>${esc(launched.log)}</code></div>` : ""}
    </div>` : "";

    $("#stream").innerHTML = msgs + card;
    if (form) {
      const on = (id, key, cast) => {
        const el = $(id);
        if (!el) return;
        el.onchange = () => { form[key] = cast ? cast(el.value) : el.value; refreshPreview(); };
      };
      on("#f-ds", "dataset");
      on("#f-h", "harness");
      on("#f-r", "rounds", Number);
      on("#f-j", "jobs", Number);
      on("#f-t", "trials", Number);
      const imp = $("#f-imp");
      if (imp) imp.onchange = () => {
        const [name, model] = imp.value.split("|");
        form.improver = name; form.improver_model = model; refreshPreview();
      };
      const btn = $("#confirm");
      if (btn) btn.onclick = confirmLaunch;
    }
  }

  async function confirmLaunch() {
    const btn = $("#confirm");
    btn.disabled = true;
    try {
      const r = await fetch("/api/runs", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset: form.dataset, harness: form.harness, improver: form.improver,
          improver_model: form.improver_model, rounds: Number(form.rounds), jobs: Number(form.jobs),
          trials: Number(form.trials), sampling: form.sampling }) });
      const d = await r.json();
      if (r.status === 202) {
        launched = d;
        session().msgs.push({ who: "ai", text: `已启动 ${d.run_id}。它出现在「实验」列表里才会算跑起来。` });
      } else if (r.status === 409) {
        blocked = `已有 driver 在跑：${(d.live || []).map((x) => x.run_id).join("、")}（服务端拒绝，未起进程）`;
        launched = null;
      } else {
        blocked = `被拒绝：${d.detail || d.error || r.status}`;
        launched = null;
      }
    } catch (e) {
      blocked = `提交失败：${e.message}`;
    }
    persist();
    render();
    if (btn) btn.disabled = false;
  }

  /* ── 交互 ─────────────────────────────────────────── */
  function addSkill(text) {
    if (text) session().msgs.push({ who: "user", text });
    session().msgs.push({ who: "ai", text: "把要跑的东西填一下；确认后由平台起跑。" });
    if (!session().title || session().title === "新的运行") session().title = (text || "新的运行").slice(0, 18);
    persist();
    if (form) refreshPreview(); else init();
  }

  async function init() {
    window.FORM = await loadForm();
    await refreshPreview();
  }

  $("#add-skill").onclick = () => addSkill($("#say").value.trim());
  $("#send").onclick = () => {
    const t = $("#say").value.trim();
    $("#say").value = "";
    addSkill(t);
  };
  $("#say").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#send").click(); }
  });

  (async () => {
    try {
      window.FORM = await loadForm();
      const health = await (await fetch("/api/health")).json();
      $("#st2").innerHTML = `<span class="status-dot" data-tone="ok"></span>平台 <b>${esc(String(health.platform_content_sha || "").slice(0, 12))}</b>`;
      $("#st3").innerHTML = (health.running || []).length
        ? `<span class="status-dot" data-tone="warn"></span>${health.running.length} 个 driver 在跑`
        : `<span class="status-dot" data-tone="ok"></span>没有 driver 在跑`;
      $("#n2").textContent = String((await (await fetch("/api/runs")).json()).count ?? "—");
      if (!session().msgs.length) addSkill("");
      else if (form) await refreshPreview();
      render();
    } catch (e) {
      $("#stream").innerHTML = `<div class="err">API 不可达：${esc(e.message)}<br>启动：<code>python3 console/server.py --port 4450</code></div>`;
    }
  })();
})();
