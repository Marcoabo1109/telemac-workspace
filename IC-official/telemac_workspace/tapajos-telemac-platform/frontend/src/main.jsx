import React, { useEffect, useState, useRef } from "react";
import { createRoot } from "react-dom/client";
import DispersionPoC from "./components/DispersionPoC";
import NestorEditor from "./components/NestorEditor";
import MeshViewer from "./components/MeshViewer";
import TimeSeriesEditor from "./components/TimeSeriesEditor";
import "./style.css";
const api = async (path, opts = {}) => {
  const r = await fetch("/api" + path, opts);
  if (!r.ok) {
    let x = await r.text();
    try {
      x = JSON.parse(x).detail;
    } catch {}
    throw Error(x);
  }
  return r;
};
export async function saveResponse(r, name) {
  const b = await r.blob(),
    url = URL.createObjectURL(b),
    a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
const upload = async (path, file) => {
  const f = new FormData();
  f.append("file", file);
  return (await api(path, { method: "POST", body: f })).json();
};
const post = (path, data) =>
  api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
function App() {
  const [tab, setTab] = useState("Dispersão · PoC"),
    [sub, setSub] = useState("Físicos"),
    [params, setParams] = useState({}),
    [schema, setSchema] = useState(null),
    [mesh, setMesh] = useState(null),
    [qsl, setQsl] = useState(null),
    [cli, setCli] = useState([]),
    [edits, setEdits] = useState({}),
    [meshFile, setMeshFile] = useState(null),
    [files, setFiles] = useState([]),
    [job, setJob] = useState(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [healthy, setHealthy] = useState(null),
    [dataCatalog, setDataCatalog] = useState(null),
    [example, setExample] = useState("tapajos"),
    [busy, setBusy] = useState(false),
    [frame, setFrame] = useState(0),
    [geom, setGeom] = useState(null),
    [sizes, setSizes] = useState({
      lc_canal: 200,
      lc_planicie: 800,
      lc_fronteira: 200,
    });
  const act =
    (fn) =>
    async (...args) => {
      setError("");
      setBusy(true);
      try {
        await fn(...args);
      } catch (e) {
        setError(e.message);
      } finally {
        setBusy(false);
      }
    };
  const init = async (caseId = "tapajos") => {
    const [s, e, h, d] = await Promise.all([
      api("/schema").then((r) => r.json()),
      api(`/example?case_id=${caseId}`).then((r) => r.json()),
      api("/health").then((r) => r.json()),
      api("/data/catalog").then((r) => r.json()),
    ]);
    setSchema(s);
    setParams(e.params);
    setMesh(e.mesh);
    setQsl(e.qsl);
    setCli(e.cli);
    setHealthy(h);
    setDataCatalog(d);
    const geometryName = e.params["GEOMETRY FILE"].replaceAll("\'", "");
    setFiles([]);
    setJob(null);
    setMeshFile(
      new File(
        [
          await (
            await api(`/example/${geometryName}?case_id=${caseId}`)
          ).blob(),
        ],
        geometryName,
      ),
    );
    setExample(caseId);
    setEdits({});
    setFrame(0);
    setNotice(
      caseId === "tapajos"
        ? "Tapajós exploratório: eixo OSM; largura, fundo, vazão e datum assumidos. Traçador normalizado, sem calibração."
        : "Caso Culm carregado. Referência numérica, não representa o Tapajós.",
    );
  };
  useEffect(() => {
    act(init)();
  }, []);
  const change = (k, v) =>
    setParams((p) => {
      const next = { ...p, [k]: v };
      if (
        k === "LAW OF BOTTOM FRICTION" &&
        ((+p[k] === 3 && +v === 4) || (+p[k] === 4 && +v === 3)) &&
        +p["FRICTION COEFFICIENT"] > 0
      )
        next["FRICTION COEFFICIENT"] = String(1 / +p["FRICTION COEFFICIENT"]);
      return next;
    });
  const fileInput = (label, accept, fn, multiple = false) => (
    <label className="button secondary">
      {label}
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={act(async (e) => {
          if (e.target.files.length)
            await fn(multiple ? [...e.target.files] : e.target.files[0]);
          e.target.value = "";
        })}
      />
    </label>
  );
  const exportMesh = async () => {
    const form = new FormData();
    form.append("file", meshFile);
    form.append("edits", JSON.stringify(edits));
    return api("/mesh/export", { method: "POST", body: form });
  };
  const groups = {
    Físicos: [
      "LAW OF BOTTOM FRICTION",
      "FRICTION COEFFICIENT",
      "VELOCITY DIFFUSIVITY",
      "TURBULENCE MODEL",
    ],
    Contorno: [
      "GEOMETRY FILE",
      "BOUNDARY CONDITIONS FILE",
      "LIQUID BOUNDARIES FILE",
      "PREVIOUS COMPUTATION FILE",
      "PRESCRIBED FLOWRATES",
      "PRESCRIBED ELEVATIONS",
    ],
    Numéricos: [
      "TIME STEP",
      "NUMBER OF TIME STEPS",
      "SOLVER",
      "SOLVER ACCURACY",
      "IMPLICITATION FOR DEPTH",
      "IMPLICITATION FOR VELOCITY",
    ],
    Módulos: [
      "TITLE",
      "RESULTS FILE",
      "VARIABLES FOR GRAPHIC PRINTOUTS",
      "COMPUTATION CONTINUED",
      "TIDAL FLATS",
    ],
  };
  const tips = {
    "FRICTION COEFFICIENT":
      "Strickler: m⅓/s; Manning: s/m⅓. n = 1/Ks. Calibre com observações.",
    "VELOCITY DIFFUSIVITY": "Difusividade horizontal em m²/s.",
    "TIME STEP":
      "Passo de integração em segundos; verificar estabilidade e convergência.",
    "SOLVER ACCURACY": "Tolerância do sistema linear, distinta do erro físico.",
    "PRESCRIBED FLOWRATES":
      "m³/s, valores separados por ; na ordem das fronteiras líquidas.",
    "PRESCRIBED ELEVATIONS": "Metros no mesmo datum vertical da batimetria.",
  };
  const launch = act(async () => {
    const f = new FormData();
    f.append("params", JSON.stringify(params));
    if (example) f.append("example", example);
    for (const file of files) f.append("files", file);
    if (meshFile) {
      const b = Object.keys(edits).length
        ? await (await exportMesh()).blob()
        : meshFile;
      f.append(
        "files",
        b,
        String(params["GEOMETRY FILE"] || meshFile.name).replaceAll("'", ""),
      );
    }
    if (qsl)
      f.append(
        "files",
        await (await post("/qsl/export", qsl)).blob(),
        String(params["LIQUID BOUNDARIES FILE"] || "boundaries.qsl").replaceAll(
          "'",
          "",
        ),
      );
    if (cli.length)
      f.append(
        "files",
        await (await post("/cli/export", cli)).blob(),
        String(params["BOUNDARY CONDITIONS FILE"] || "boundary.cli").replaceAll(
          "'",
          "",
        ),
      );
    const { id } = await (
      await api("/jobs", { method: "POST", body: f })
    ).json();
    setJob({ id, status: "queued", progress: 0, logs: [] });
    const ws = new WebSocket(
      `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/jobs/${id}/ws`,
    );
    ws.onmessage = (e) => {
      const d = JSON.parse(e.data);
      setJob((j) => ({ ...j, ...d, logs: [...j.logs, ...d.logs] }));
    };
    ws.onerror = () =>
      setError("Conexão de logs interrompida. Consulte /api/jobs/" + id);
    setTab("Simulação");
  });
  return (
    <div className="layout">
      <aside>
        <div className="brand">
          <span className="brandmark">≈</span>
          <div>
            TAPAJÓS<small>LABORATÓRIO DE RIOS</small>
          </div>
        </div>
        <div className="navlabel">ÁREA DE TRABALHO</div>
        <nav>
          {[
            "Dispersão · PoC",
            "Visão geral",
            "Parâmetros",
            "Malha e batimetria",
            "Séries temporais",
            "Fronteiras",
            "GAIA / Nestor",
            "Simulação",
            "Dados e ciência",
          ].map((t, i) => (
            <button
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => setTab(t)}
            >
              <span>{["◉", "◈", "⚙", "△", "∿", "⌁", "≈", "▷", "⊙"][i]}</span>
              {t}
            </button>
          ))}
        </nav>
        <div className="asidebottom">
          <span className="dot" /> ICMC · USP / LMACC
          <small>
            Iniciação científica · 2026
            <br />
            Open TELEMAC-MASCARET
          </small>
        </div>
      </aside>
      <main className={tab === "Dispersão · PoC" ? "poc-page" : ""}>
        <header>
          <span>PROJETO / DISPERSÃO DE METAIS</span>
          <span className="tag">
            {example === "tapajos"
              ? "Tapajós · hipóteses"
              : example
                ? "Culm · referência"
                : "Caso importado"}
          </span>
        </header>
        <div className="heading">
          <div>
            <div className="eyebrow">HIDRODINÂMICA & TRANSPORTE</div>
            <h1>{tab === "Visão geral" ? "Do rio ao modelo." : tab}</h1>
            <p>
              {tab === "Visão geral"
                ? "Prepare, explore e simule escoamentos de superfície livre."
                : "Configuração rastreável para cada etapa do experimento."}
            </p>
          </div>
          <button
            disabled={busy}
            onClick={act(() => init("tapajos"))}
            className="secondary"
          >
            ↻ Carregar Tapajós
          </button>
          <button
            disabled={busy}
            onClick={act(() => init("culm"))}
            className="secondary"
          >
            ↻ Carregar Culm
          </button>
        </div>
        {error && (
          <div role="alert" className="error">
            {error}
          </div>
        )}
        {notice && (
          <div className="notice">
            {notice}
            <button onClick={() => setNotice("")}>×</button>
          </div>
        )}
        {tab === "Dispersão · PoC" && <DispersionPoC />}
        {tab === "Visão geral" && (
          <>
            <div className="stats">
              <article>
                <small>NÓS DA MALHA</small>
                <strong>{mesh?.x.length.toLocaleString("pt-BR") || "—"}</strong>
                <span>SERAFIN · triangular 2D</span>
              </article>
              <article>
                <small>ELEMENTOS</small>
                <strong>
                  {mesh?.triangles.length.toLocaleString("pt-BR") || "—"}
                </strong>
                <span>Geometria do caso ativo</span>
              </article>
              <article>
                <small>TEMPO SIMULADO</small>
                <strong>
                  {(
                    ((+params["TIME STEP"] || 0) *
                      (+params["NUMBER OF TIME STEPS"] || 0)) /
                    3600
                  ).toFixed(1)}{" "}
                  <em>h</em>
                </strong>
                <span>
                  {params["NUMBER OF TIME STEPS"]} passos · Δt{" "}
                  {params["TIME STEP"]} s
                </span>
              </article>
              <article>
                <small>MOTOR NUMÉRICO</small>
                <strong className="smaller">TELEMAC-2D</strong>
                <span>
                  {healthy?.runner_configured
                    ? "Configurado para execução"
                    : "Configuração pendente"}
                </span>
              </article>
            </div>
            <section>
              <div className="sectiontitle">
                <div>
                  <h2>Território computacional</h2>
                  <p>
                    Batimetria do caso{" "}
                    {example === "tapajos"
                      ? "Tapajós (hipótese)"
                      : example
                        ? "Culm"
                        : "importado"}{" "}
                    · coordenadas da malha
                  </p>
                </div>
                <button
                  className="secondary"
                  onClick={() => setTab("Malha e batimetria")}
                >
                  Explorar malha ↗
                </button>
              </div>
              <MeshViewer
                mesh={mesh}
                edits={edits}
                onEdit={() => {}}
                cli={cli}
              />
            </section>
            <div className="twocol">
              <section>
                <span className="eyebrow">PRÓXIMO EXPERIMENTO</span>
                <h2>Uma base verificável</h2>
                <p>
                  Confira os parâmetros e as fronteiras antes da execução. O
                  exemplo Culm permite testar o fluxo completo sem dados
                  externos.
                </p>
                <button onClick={() => setTab("Parâmetros")}>
                  Configurar experimento →
                </button>
              </section>
              <section>
                <span className="eyebrow">RIO TAPAJÓS</span>
                <h2>Dados antes da calibração</h2>
                <p>
                  Eixo OSM, estatísticas SGB e 14.361 cotas diárias consistidas
                  da ANA coletados. Vazão, batimetria, margens e datum ainda
                  bloqueiam a calibração.
                </p>
                <button
                  className="secondary"
                  onClick={() => setTab("Dados e ciência")}
                >
                  Ver fundamentação →
                </button>
              </section>
            </div>
          </>
        )}
        <div hidden={tab !== "GAIA / Nestor"}>
          <NestorEditor hydro={params} />
        </div>
        {tab === "Parâmetros" && (
          <section>
            <div className="toolbar">
              {fileInput("Importar .cas", ".cas", async (f) => {
                setParams(await upload("/cas/import", f));
                setExample(false);
                setMesh(null);
                setMeshFile(null);
                setQsl(null);
                setCli([]);
                setFiles([]);
                setEdits({});
                setNotice(
                  "Importe a geometria, CLI, séries e demais arquivos do novo caso.",
                );
              })}
              <button
                onClick={act(async () =>
                  saveResponse(await post("/cas/export", params), "case.cas"),
                )}
              >
                Exportar Steering File
              </button>
            </div>
            <div className="tabs">
              {Object.keys(groups).map((g) => (
                <button
                  className={sub === g ? "selected" : ""}
                  onClick={() => setSub(g)}
                  key={g}
                >
                  {g}
                </button>
              ))}
            </div>
            <div className="formgrid">
              {groups[sub].map((k) => (
                <label key={k} title={tips[k] || k}>
                  <span>{k} ⓘ</span>
                  {schema?.choices[k] ? (
                    <select
                      value={params[k] ?? ""}
                      onChange={(e) => change(k, e.target.value)}
                    >
                      {Object.entries(schema.choices[k]).map(([v, n]) => (
                        <option key={v} value={v}>
                          {v} · {n}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      value={params[k] ?? ""}
                      onChange={(e) => change(k, e.target.value)}
                    />
                  )}
                  {k === "FRICTION COEFFICIENT" && (
                    <input
                      aria-label="Ajuste de rugosidade"
                      type="range"
                      min={
                        +params["LAW OF BOTTOM FRICTION"] === 4 ? 0.001 : 0.1
                      }
                      max={Math.max(
                        +params["FRICTION COEFFICIENT"] || 0,
                        +params["LAW OF BOTTOM FRICTION"] === 4 ? 0.2 : 100,
                      )}
                      step={
                        +params["LAW OF BOTTOM FRICTION"] === 4 ? 0.001 : 0.1
                      }
                      value={+params[k] || 0}
                      onChange={(e) => change(k, e.target.value)}
                    />
                  )}
                  <small>{tips[k] || "Palavra-chave TELEMAC"}</small>
                </label>
              ))}
            </div>
            {sub === "Módulos" && (
              <p className="notice">
                Configure os arquivos sedimentares e de dragagem na aba GAIA /
                Nestor. O pacote é exportado para execução pelo CLI TELEMAC.
                Transporte reativo permanece uma etapa futura.
              </p>
            )}
            <details>
              <summary>
                Todas as palavras-chave ({Object.keys(params).length})
              </summary>
              <textarea
                rows="18"
                value={Object.entries(params)
                  .map(([k, v]) => `${k} = ${v}`)
                  .join("\n")}
                readOnly
              />
            </details>
          </section>
        )}
        {tab === "Malha e batimetria" && (
          <section>
            <div className="toolbar">
              {fileInput("Importar .slf", ".slf", async (f) => {
                setMesh(await upload("/mesh/import", f));
                setMeshFile(f);
                change("GEOMETRY FILE", f.name);
                setEdits({});
                setFrame(0);
              })}
              <button
                disabled={!meshFile}
                onClick={act(async () =>
                  saveResponse(await exportMesh(), "mesh_edited.slf"),
                )}
              >
                Exportar .slf editado
              </button>
              {fileInput("Interpolar DEM", ".tif,.tiff,.asc", async (f) => {
                const crs = window.prompt(
                  "CRS da malha (por exemplo EPSG:32721)",
                );
                if (!crs) return;
                const form = new FormData();
                form.append("file", meshFile);
                form.append("dem", f);
                form.append("mesh_crs", crs);
                const d = await (
                  await api("/mesh/dem", { method: "POST", body: form })
                ).json();
                setEdits(d.edits);
                setNotice(d.warning);
              })}
            </div>
            <MeshViewer
              mesh={mesh}
              edits={edits}
              onEdit={(i, z) => setEdits((x) => ({ ...x, [i]: z }))}
              cli={cli}
              editable
            />
            <p>
              {Object.keys(edits).length} nós editados. Coordenadas e cotas
              devem compartilhar referências compatíveis.
            </p>
            {mesh?.times.length > 1 && (
              <label>
                Instante {mesh.times[frame]} s
                <input
                  type="range"
                  min="0"
                  max={mesh.times.length - 1}
                  value={frame}
                  onChange={act(async (e) => {
                    const n = +e.target.value;
                    setFrame(n);
                    setMesh(await upload("/mesh/import?frame=" + n, meshFile));
                  })}
                />
              </label>
            )}
            <details>
              <summary>Gerar malha GMSH a partir de polígono GeoJSON</summary>
              <p>
                O domínio deve ser um polígono fechado em WGS84. Uma linha de
                centro exige margens ou largura explícita.
              </p>
              {fileInput("Carregar domínio", ".json,.geojson", async (f) =>
                setGeom(JSON.parse(await f.text())),
              )}
              <div className="formgrid">
                {Object.keys(sizes).map((k) => (
                  <label key={k}>
                    {k} [m]
                    <input
                      type="number"
                      min="1"
                      value={sizes[k]}
                      onChange={(e) =>
                        setSizes((s) => ({ ...s, [k]: +e.target.value }))
                      }
                    />
                  </label>
                ))}
              </div>
              <button
                disabled={!geom}
                onClick={act(async () =>
                  saveResponse(
                    await post("/mesh/generate", { geometry: geom, ...sizes }),
                    "mesh.zip",
                  ),
                )}
              >
                Gerar e baixar malha
              </button>
            </details>
          </section>
        )}
        {tab === "Séries temporais" && (
          <section>
            <div className="toolbar">
              {fileInput("Importar .qsl", ".qsl,.liq", async (f) => {
                setQsl(await upload("/qsl/import", f));
                change("LIQUID BOUNDARIES FILE", f.name);
              })}
              <button
                disabled={!qsl}
                onClick={act(async () =>
                  saveResponse(
                    await post("/qsl/export", qsl),
                    "boundaries.qsl",
                  ),
                )}
              >
                Exportar .qsl
              </button>
            </div>
            <TimeSeriesEditor qsl={qsl} onChange={setQsl} onError={setError} />
          </section>
        )}
        {tab === "Fronteiras" && (
          <section>
            <div className="toolbar">
              {fileInput("Importar .cli", ".cli", async (f) => {
                setCli(await upload("/cli/import", f));
                change("BOUNDARY CONDITIONS FILE", f.name);
              })}
              <button
                onClick={act(async () =>
                  saveResponse(await post("/cli/export", cli), "boundary.cli"),
                )}
              >
                Exportar .cli
              </button>
            </div>
            <MeshViewer mesh={mesh} edits={edits} onEdit={() => {}} cli={cli} />
            <p>
              A ordem do CLI determina as fronteiras líquidas Q(n)/SL(n).
              Confira a continuidade dos segmentos.
            </p>
            <div className="tablewrap">
              <table>
                <thead>
                  <tr>
                    <th>Nó</th>
                    <th>LIHBOR / LIUBOR / LIVBOR</th>
                    <th>Tipo</th>
                  </tr>
                </thead>
                <tbody>
                  {cli.map((r, i) => (
                    <tr key={i}>
                      <td>{r[11]}</td>
                      <td>{r.slice(0, 3).join(" / ")}</td>
                      <td>
                        <select
                          value={r.slice(0, 3).join(",")}
                          onChange={(e) =>
                            setCli((a) =>
                              a.map((row, j) =>
                                j === i
                                  ? [
                                      ...e.target.value.split(",").map(Number),
                                      ...row.slice(3),
                                    ]
                                  : row,
                              ),
                            )
                          }
                        >
                          <option value="2,2,2">Parede</option>
                          <option value="4,5,5">Entrada · vazão</option>
                          <option value="5,4,4">Saída · nível</option>
                          {!["2,2,2", "4,5,5", "5,4,4"].includes(
                            r.slice(0, 3).join(","),
                          ) && (
                            <option value={r.slice(0, 3).join(",")}>
                              Outro (preservado)
                            </option>
                          )}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
        {tab === "Simulação" && (
          <section>
            <h2>Executar experimento</h2>
            <p>
              Os arquivos são copiados para uma pasta exclusiva por execução.
              Edite o número de passos para um teste curto.
            </p>
            <div className="toolbar">
              {fileInput(
                "Adicionar arquivos do caso",
                ".slf,.cli,.qsl,.txt,.liq",
                setFiles,
                true,
              )}
              <button
                disabled={busy || ["queued", "running"].includes(job?.status)}
                onClick={launch}
              >
                ▷ Executar TELEMAC-2D
              </button>
              <button
                className="secondary"
                onClick={() => {
                  change("NUMBER OF TIME STEPS", "20");
                  change("GRAPHIC PRINTOUT PERIOD", "5");
                  change("LISTING PRINTOUT PERIOD", "5");
                  setNotice(
                    "Teste curto: 20 passos. Isso não calibra nem valida o rio.",
                  );
                }}
              >
                Configurar teste curto
              </button>
            </div>
            <p>{files.map((f) => f.name).join(", ")}</p>
            {job && (
              <>
                <div className="sectiontitle">
                  <h3>{job.status}</h3>
                  <span>{job.progress.toFixed(0)}%</span>
                </div>
                <progress max="100" value={job.progress} />
                <pre className="log">
                  {job.logs.join("\n") || "Preparando execução…"}
                </pre>
                {job.status === "completed" && (
                  <div className="toolbar">
                    <a
                      className="button"
                      href={"/api/jobs/" + job.id + "/result"}
                    >
                      Baixar resultados .slf
                    </a>
                    <button
                      className="secondary"
                      onClick={act(async () => {
                        const f = new File(
                          [
                            await (
                              await api("/jobs/" + job.id + "/result")
                            ).blob(),
                          ],
                          "results.slf",
                        );
                        setMesh(await upload("/mesh/import", f));
                        setMeshFile(f);
                        setEdits({});
                        setFrame(0);
                        setTab("Malha e batimetria");
                      })}
                    >
                      Visualizar resultados
                    </button>
                  </div>
                )}
              </>
            )}
          </section>
        )}
        {tab === "Dados e ciência" && (
          <>
            <section>
              <h2>Inventário científico dos dados</h2>
              {dataCatalog && (
                <>
                  <div className="catalogstats">
                    <article>
                      <strong>{dataCatalog.report.counts.available}</strong>
                      <span>dados disponíveis</span>
                    </article>
                    <article>
                      <strong>{dataCatalog.report.counts.derived}</strong>
                      <span>produtos derivados</span>
                    </article>
                    <article className="blocked">
                      <strong>{dataCatalog.report.counts.missing}</strong>
                      <span>requisitos ausentes</span>
                    </article>
                  </div>
                  <h3>Marcos de prontidão</h3>
                  <div className="gategrid">
                    {dataCatalog.report.gates.map((gate) => (
                      <article key={gate.id}>
                        <span className={`gate ${gate.status}`}>
                          {gate.status === "ready" ? "PRONTO" : "BLOQUEADO"}
                        </span>
                        <h3>{gate.title}</h3>
                        {gate.blocked_by.length > 0 && (
                          <p>
                            Faltam:{" "}
                            {gate.blocked_by
                              .map((item) => item.title)
                              .join(", ")}
                          </p>
                        )}
                      </article>
                    ))}
                  </div>
                  <h3>Fase 3 · levantamento de dados reais</h3>
                  <div className="phase3grid">
                    {dataCatalog.phase3.observed_series.map((series) => (
                      <article key={series.id}>
                        <span className="gate ready">ADQUIRIDO</span>
                        <h3>{series.title}</h3>
                        <strong>
                          {series.quality.records.toLocaleString("pt-BR")}
                        </strong>
                        <p>
                          observações entre {series.quality.start} e{" "}
                          {series.quality.end} ·{" "}
                          {series.quality.completeness_percent}% completas
                        </p>
                        <p>
                          {series.quality.missing_days} dias ausentes · maior
                          lacuna: {series.quality.maximum_gap_days} dias
                        </p>
                      </article>
                    ))}
                    <article className="blocked">
                      <span className="gate blocked">PENDENTE</span>
                      <h3>Próximas aquisições</h3>
                      <p>
                        A vazão diária foi adquirida. Batimetria, margens
                        verificadas e vínculo geodésico da régua continuam
                        obrigatórios para calibração.
                      </p>
                    </article>
                  </div>
                </>
              )}
              <h3>Dados coletados e primeiro cenário</h3>
              <p>
                Eixo do Tapajós: OpenStreetMap. Forçantes observadas: vazão de
                Acará do Tapajós 17650002 e cota de Itaituba 17730000. A janela
                completa de 2007 foi preparada com controles em Buburé, mas o
                cenário executável ainda usa a mediana climatológica de setembro
                (3,71 m), pois falta o datum da régua.
              </p>
              <p>
                Hipóteses: largura 1.200 m, profundidade nominal 4–8 m, vazão
                6.000 m³/s e Strickler 30. Traçador conservativo normalizado;
                sem calibração ou concentração medida de metais.
              </p>
              <a
                href="/api/example/assumptions.json?case_id=tapajos"
                target="_blank"
                rel="noreferrer"
              >
                Consultar hipóteses e fontes ↗
              </a>
              {dataCatalog && (
                <>
                  <h3>Requisitos ainda ausentes</h3>
                  <div className="tablewrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Conjunto</th>
                          <th>Categoria</th>
                          <th>Condição</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dataCatalog.catalog.datasets
                          .filter((dataset) => dataset.status === "missing")
                          .map((dataset) => (
                            <tr key={dataset.id}>
                              <td>{dataset.title}</td>
                              <td>{dataset.category}</td>
                              <td>{dataset.limitations[0]}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
              <h3>Próximos trechos</h3>
              <div className="reachgrid">
                {[
                  ["01", "Alto", "Juruena + Teles Pires"],
                  ["02", "Médio", "Jacareacanga / Itaituba"],
                  ["03", "Baixo", "Santarém / foz"],
                ].map(([n, t, d]) => (
                  <article key={n}>
                    <span className="reachnumber">{n}</span>
                    <h3>{t} Tapajós</h3>
                    <p>{d}</p>
                    <span className="tag">Aguardando dados validados</span>
                  </article>
                ))}
              </div>
              <p>
                As caixas geográficas do resumo servem à triagem; não definem a
                bacia nem substituem a localização verificada de cada estação.
              </p>
              <h3>Condições científicas</h3>
              <ul>
                <li>
                  SRTM e DEMs terrestres descrevem topografia; não fornecem
                  automaticamente o fundo submerso.
                </li>
                <li>
                  Cota da régua ANA deve ser convertida de cm para m e vinculada
                  ao datum da malha antes de prescrever SL.
                </li>
                <li>
                  Culm testa o pipeline. A calibração do Tapajós exige
                  batimetria, vazão, níveis e período observacional comum.
                </li>
                <li>
                  Metal ligado ao sedimento e metal dissolvido exigem hipóteses
                  distintas; a proporcionalidade linear é uma simplificação.
                </li>
              </ul>
              <a
                href="https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html"
                target="_blank"
                rel="noreferrer"
              >
                Documentação oficial ANA ↗
              </a>
            </section>
            <section>
              <h2>Aquisição e análise</h2>
              <p>
                Execute os módulos Python documentados no README: cliente ANA
                com token, leitura de XML histórico, seleção por trecho,
                correlação com lag, permanência e conversão .qsl. Credenciais
                ficam no ambiente do servidor.
              </p>
              <pre>
                python -m scripts.data_catalog
                <br />
                python -m scripts.phase3_data --help
                <br />
                python -m scripts.tapajos_data --help
                <br />
                python -m scripts.convert_to_telemac --help
                <br />
                python -m scripts.mesh_generator --help
              </pre>
            </section>
          </>
        )}
        <footer>
          Marco Antonio Bicalho de Oliveira · Orientação Prof. Roberto F. Ausas
          <span>Ciência reproduzível / v0.1</span>
        </footer>
      </main>
    </div>
  );
}
createRoot(document.getElementById("root")).render(<App />);
