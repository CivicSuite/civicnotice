"""Static public UI shell for CivicNotice v0.1.2."""

from __future__ import annotations


def render_public_lookup_page() -> str:
    """Render the public-facing CivicNotice sample page."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CivicNotice Public Notice Support</title>
<style>
  :root { --ink:#17202a; --muted:#5c6470; --blue:#244f73; --green:#2f654c; --gold:#d8ad48; --line:#ccd5df; }
  * { box-sizing: border-box; }
  html, body { max-width:100%; overflow-x:hidden; }
  body { margin:0; color:var(--ink); font-family:"Aptos","Segoe UI",sans-serif; background:linear-gradient(135deg,#fff8ed,#eef8ff); }
  .skip-link { position:absolute; left:1rem; top:-4rem; background:var(--ink); color:white; padding:.7rem 1rem; border-radius:999px; }
  .skip-link:focus { top:1rem; }
  header, main, footer { width:100%; max-width:1120px; margin:0 auto; padding-left:16px; padding-right:16px; }
  header { padding:48px 0 24px; }
  .eyebrow { color:var(--blue); text-transform:uppercase; letter-spacing:.18em; font-weight:800; font-size:.78rem; }
  h1 { max-width:980px; margin:0; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2.2rem,7vw,5.4rem); line-height:1.02; letter-spacing:-.04em; overflow-wrap:break-word; word-break:break-word; }
  .lede { max-width:840px; font-size:clamp(1.1rem,2.4vw,1.45rem); line-height:1.55; color:#31404a; }
  .badge { display:inline-flex; width:fit-content; padding:.45rem .75rem; border-radius:999px; background:var(--green); color:white; font-weight:900; }
  .grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:18px; min-width:0; }
  .card { grid-column:span 6; min-width:0; max-width:100%; padding:24px; border:1px solid var(--line); border-radius:28px; background:rgba(255,255,255,.92); box-shadow:0 18px 40px rgba(35,43,50,.10); }
  .card.large { grid-column:span 12; }
  h2,h3 { font-family:Georgia,"Times New Roman",serif; letter-spacing:-.03em; }
  h2 { margin:0 0 14px; font-size:clamp(1.8rem,4vw,3rem); }
  p, li { line-height:1.65; overflow-wrap:anywhere; }
  textarea, button { width:100%; max-width:100%; min-width:0; border:1px solid #b9c6cc; border-radius:16px; padding:.85rem 1rem; font:inherit; }
  textarea { background:#f7f8fb; color:var(--ink); }
  button { width:fit-content; min-width:190px; border:0; background:var(--blue); color:white; font-weight:900; cursor:default; }
  .result { margin-top:18px; padding:18px; border-left:6px solid var(--green); border-radius:18px; background:white; }
  .warning { border-left-color:#b2603f; background:#fff8f4; }
  .kicker { color:var(--muted); font-size:.86rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }
  footer { padding:38px 0 56px; color:var(--muted); }
  :focus-visible { outline:4px solid var(--gold); outline-offset:3px; }
  @media (max-width:760px) { header{padding-top:34px}h1{font-size:clamp(1.95rem,10vw,2.55rem)}.lede{font-size:1.02rem}.card{grid-column:span 12;padding:20px;border-radius:22px}button{width:100%;white-space:normal} }
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header>
  <p class="eyebrow">CivicSuite / CivicNotice public sample</p>
  <h1>Public notices with fewer missed deadlines.</h1>
  <p class="lede">CivicNotice demonstrates notice administration support: registry stubs, deadline plans, publication-readiness checks, channel planning, and proof-preserving records exports without publishing official notice.</p>
  <p><span class="badge">v0.1.2 notice compliance foundation</span></p>
</header>
<main id="main" tabindex="-1">
  <section class="grid" aria-labelledby="lookup-title">
    <article class="card large">
      <p class="kicker">Sample hearing notice</p>
      <h2 id="lookup-title">Planning hearing notice</h2>
      <textarea aria-label="Sample notice notes" rows="4">Public hearing on rezoning request. Confirm statutory authority, publication lead time, accessibility needs, and proof of publication.</textarea>
      <button type="button">Draft sample notice file</button>
      <div class="result" role="status" aria-live="polite">
        <h3>Staff review packet</h3>
        <ul><li>Confirm statutory authority, publication channel, lead time, and reviewer.</li><li>Route draft copy for clerk/legal review before publication.</li><li>Preserve final notice, proof, screenshots, invoices, and source matter.</li></ul>
      </div>
    </article>
    <article class="card"><p class="kicker">Deadlines</p><h2>Lead-time reminders</h2><div class="result"><p>CivicNotice calculates review milestones; staff verify the legal deadline.</p></div></article>
    <article class="card"><p class="kicker">Channels</p><h2>Publication path</h2><div class="result"><p>Channel helpers surface website, posting board, newspaper, agenda page, and accessibility review needs.</p></div></article>
    <article class="card"><p class="kicker">Proof</p><h2>Records-ready</h2><div class="result"><p>Exports preserve draft, final notice, approvals, proof, source matter, and reviewer metadata.</p></div></article>
    <article class="card large"><p class="kicker">Boundary</p><h2>No official publication</h2><div class="result warning"><p>CivicNotice does not determine legal sufficiency, publish official notices, provide legal advice, call live LLMs, write back to publication systems, or replace the notice system of record.</p></div></article>
  </section>
</main>
<footer><p>CivicNotice is part of the Apache 2.0 CivicSuite open-source municipal AI project.</p></footer>
</body>
</html>
"""


def render_staff_page() -> str:
    """Render the staff-facing CivicNotice work queue page."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CivicNotice Staff Review</title>
<style>
  :root { --ink:#17202a; --muted:#5c6470; --blue:#244f73; --green:#2f654c; --gold:#d8ad48; --line:#ccd5df; --paper:#fbfdff; }
  * { box-sizing:border-box; }
  html, body { max-width:100%; overflow-x:hidden; }
  body { margin:0; color:var(--ink); font-family:"Aptos","Segoe UI",sans-serif; background:#f3f8fb; }
  main, header, footer { width:100%; max-width:980px; margin:0 auto; padding-left:16px; padding-right:16px; }
  header { padding:42px 0 22px; }
  .eyebrow { color:var(--blue); text-transform:uppercase; letter-spacing:.16em; font-weight:900; font-size:.78rem; }
  h1 { margin:.2rem 0 .6rem; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2rem,6vw,4.2rem); line-height:1.04; overflow-wrap:anywhere; }
  .lede { max-width:760px; color:#31404a; font-size:1.15rem; line-height:1.55; }
  .panel { border:1px solid var(--line); border-radius:8px; background:var(--paper); padding:20px; box-shadow:0 14px 32px rgba(35,43,50,.08); }
  .stack { display:grid; gap:16px; }
  label { display:grid; gap:6px; font-weight:900; }
  input, textarea, button { width:100%; border:1px solid #b9c6cc; border-radius:8px; padding:.82rem 1rem; font:inherit; }
  textarea { min-height:88px; resize:vertical; }
  button { border:0; background:var(--blue); color:white; font-weight:900; cursor:pointer; }
  button.secondary { background:var(--green); }
  .result { padding:16px; border-left:5px solid var(--green); border-radius:8px; background:white; min-height:54px; }
  .queue { display:grid; gap:10px; }
  .queue article { border:1px solid var(--line); border-radius:8px; background:white; padding:14px; }
  footer { padding:34px 16px 54px; color:var(--muted); }
  :focus-visible { outline:4px solid var(--gold); outline-offset:3px; }
  @media (max-width:720px) { header{padding-top:28px}.panel{padding:18px} }
</style>
</head>
<body>
<header>
  <p class="eyebrow">CivicSuite / CivicNotice staff</p>
  <h1>Notice review queue</h1>
  <p class="lede">Create local notice registry records, deadline plans, and staff queue items before publication, legal sufficiency review, proof capture, or records export work.</p>
</header>
<main class="stack">
  <section class="panel stack" aria-labelledby="intake-title">
    <h2 id="intake-title">Notice review intake</h2>
    <label>Staff API key<input id="staffKey" type="password" autocomplete="off"></label>
    <label>Notice ID<input id="noticeId" value="NOTICE-001"></label>
    <label>Notice type<input id="noticeType" value="public hearing"></label>
    <label>Owner<input id="owner" value="Clerk"></label>
    <label>Review reason<textarea id="reviewReason">Confirm statutory authority, lead time, publication channel, accessibility needs, and proof capture.</textarea></label>
    <button id="saveNotice" type="button">Save notice and queue review</button>
    <button class="secondary" id="createDeadline" type="button">Create deadline review</button>
    <button class="secondary" id="loadQueue" type="button">Load review queue</button>
    <div class="result" id="status" role="status" aria-live="polite">Ready.</div>
  </section>
  <section class="panel">
    <h2>Open notice reviews</h2>
    <div class="queue" id="queue"></div>
  </section>
</main>
<footer><p>CivicNotice keeps notice work local. Staff remain responsible for legal sufficiency, publication, proof retention, and the official notice record.</p></footer>
<script>
(() => {
  const keyInput = document.querySelector("#staffKey");
  const noticeId = document.querySelector("#noticeId");
  const noticeType = document.querySelector("#noticeType");
  const owner = document.querySelector("#owner");
  const reviewReason = document.querySelector("#reviewReason");
  const status = document.querySelector("#status");
  const queue = document.querySelector("#queue");

  const headers = () => ({
    "Content-Type": "application/json",
    "X-CivicNotice-Role": "staff",
    "X-CivicNotice-Staff-Key": keyInput.value.trim()
  });

  const setStatus = (message) => {
    status.replaceChildren(document.createTextNode(message));
  };

  const renderQueue = (items) => {
    queue.replaceChildren();
    if (!items.length) {
      queue.append(document.createTextNode("No open reviews."));
      return;
    }
    for (const item of items) {
      const article = document.createElement("article");
      const title = document.createElement("strong");
      title.textContent = item.title;
      const meta = document.createElement("p");
      meta.textContent = `${item.notice_id} Â· ${item.status} Â· ${item.reason}`;
      article.append(title, meta);
      queue.append(article);
    }
  };

  document.querySelector("#saveNotice").addEventListener("click", async () => {
    try {
      const notice = await fetch("/api/v1/civicnotice/registry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          notice_id: noticeId.value.trim(),
          notice_type: noticeType.value.trim(),
          owner: owner.value.trim()
        })
      });
      const noticeJson = await notice.json();
      if (!notice.ok) throw new Error(JSON.stringify(noticeJson));
      const review = await fetch("/api/v1/civicnotice/staff/reviews", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          notice_id: noticeJson.notice_id,
          title: `Notice review: ${noticeJson.notice_type}`,
          reason: reviewReason.value.trim()
        })
      });
      const reviewJson = await review.json();
      if (!review.ok) throw new Error(JSON.stringify(reviewJson));
      setStatus(`Queued ${reviewJson.review_id} for ${noticeJson.notice_id}.`);
    } catch (error) {
      setStatus(`Could not queue notice review: ${error.message}`);
    }
  });

  document.querySelector("#createDeadline").addEventListener("click", async () => {
    try {
      const response = await fetch("/api/v1/civicnotice/deadlines", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          notice_type: noticeType.value.trim(),
          event_date: "2026-05-20",
          lead_days: 10
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data));
      setStatus(`Created deadline plan ${data.plan_id}.`);
    } catch (error) {
      setStatus(`Could not create deadline review: ${error.message}`);
    }
  });

  document.querySelector("#loadQueue").addEventListener("click", async () => {
    try {
      const response = await fetch("/api/v1/civicnotice/staff/reviews", { headers: headers() });
      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data));
      renderQueue(data.items);
      setStatus(`Loaded ${data.items.length} review item(s).`);
    } catch (error) {
      setStatus(`Could not load staff queue: ${error.message}`);
    }
  });
})();
</script>
</body>
</html>
"""

