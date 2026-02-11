const $ = (id) => document.getElementById(id);

const statusEl = $("status");
const cypherEl = $("cypher");
const executionEl = $("execution");
const contextEl = $("context");
const latencyEl = $("latency");
const suggestionCountEl = $("suggestionCount");

function setStatus(text, type = "idle") {
  statusEl.textContent = text;
  statusEl.className = `status ${type}`;
}

async function runQuery() {
  const payload = {
    query: $("query").value,
    top_k: Number($("top_k").value),
    expand_hops: Number($("expand_hops").value),
    num_suggestions: Number($("num_suggestions").value),
    execute_best: $("execute_best").checked,
  };

  setStatus("Running...", "running");
  cypherEl.textContent = "";
  executionEl.textContent = "";
  contextEl.textContent = "";

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText);
    }

    const data = await res.json();
    latencyEl.textContent = `${data.elapsed_ms} ms`;
    suggestionCountEl.textContent = data.cypher_suggestions?.length ?? 0;

    cypherEl.textContent = JSON.stringify(data.cypher_suggestions, null, 2);
    executionEl.textContent = JSON.stringify(data.result, null, 2);
    contextEl.textContent = JSON.stringify(data.retrieved_context, null, 2);

    setStatus("Done", "ok");
  } catch (err) {
    setStatus("Error", "error");
    executionEl.textContent = err.message;
  }
}

$("run").addEventListener("click", runQuery);

setStatus("Idle", "idle");
