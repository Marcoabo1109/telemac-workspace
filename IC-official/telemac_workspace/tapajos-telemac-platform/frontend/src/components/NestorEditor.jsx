import React, { useEffect, useState } from "react";

const titles = {
  Dig_by_time: "Dragagem por tempo",
  Dump_by_time: "Despejo por tempo",
  Dig_by_criterion: "Dragagem por critério",
  Save_water_level: "Salvar nível da água",
  Backfill_to_level: "Preenchimento até nível",
};
const initial = {
  restart: false,
  actions: [],
  gaia: {
    "CLASSES TYPE OF SEDIMENT": "NCO",
    "CLASSES SEDIMENT DIAMETERS": "0.001",
    "CLASSES INITIAL FRACTION": "1.0",
    "BED LOAD FOR ALL SANDS": "YES",
    "SUSPENSION FOR ALL SANDS": "NO",
    "RESULTS FILE": "'gaia_results.slf'",
  },
  polygons: "",
  reference: "",
  restart_file: "",
};
const primary = [
  "GEOMETRY FILE",
  "BOUNDARY CONDITIONS FILE",
  "RESULTS FILE",
  "CLASSES TYPE OF SEDIMENT",
  "CLASSES SEDIMENT DIAMETERS",
  "CLASSES INITIAL FRACTION",
  "CLASSES SEDIMENT DENSITY",
  "CLASSES SETTLING VELOCITIES",
  "BED LOAD FOR ALL SANDS",
  "SUSPENSION FOR ALL SANDS",
  "BED-LOAD TRANSPORT FORMULA FOR ALL SANDS",
  "LAYERS NON COHESIVE BED POROSITY",
];
async function request(path, data) {
  const response = await fetch(
    "/api" + path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  if (!response.ok) {
    const error = await response.json();
    throw Error(error.detail || "Erro na operação");
  }
  return response;
}
function save(response, name) {
  return response.blob().then((blob) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
}
export default function NestorEditor({ hydro }) {
  const [data, setData] = useState(initial),
    [schema, setSchema] = useState(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [search, setSearch] = useState(""),
    [kind, setKind] = useState("Dig_by_time");
  const work = async (fn) => {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    work(async () => setSchema(await (await request("/nestor/schema")).json()));
  }, []);
  const change = (key, value) => setData((d) => ({ ...d, [key]: value }));
  const edit = (index, key, value) =>
    setData((d) => ({
      ...d,
      actions: d.actions.map((a, i) => {
        if (i !== index) return a;
        const next = { ...a };
        if (value === "") delete next[key];
        else next[key] = value;
        return next;
      }),
    }));
  const upload = (label, fn, accept = ".dat,.txt") => (
    <label className="button secondary">
      {label}
      <input
        type="file"
        accept={accept}
        disabled={busy}
        onChange={(e) => {
          const file = e.target.files[0];
          e.target.value = "";
          if (file) work(() => fn(file));
        }}
      />
    </label>
  );
  const gaiaField = (key) => {
    const spec = schema.gaia[key];
    return (
      <label key={key} title={spec?.help || key}>
        <span>{key}</span>
        {spec?.type === "LOGICAL" ? (
          <select
            value={data.gaia[key] || ""}
            onChange={(e) => setGaia(key, e.target.value)}
          >
            <option value="">Padrão do solver</option>
            <option>YES</option>
            <option>NO</option>
          </select>
        ) : (
          <input
            value={data.gaia[key] || ""}
            placeholder={spec?.default || "Não definido"}
            onChange={(e) => setGaia(key, e.target.value)}
          />
        )}
        <small>
          {spec?.type} · padrão oficial: {spec?.default || "(vazio)"}
        </small>
        {spec?.help && (
          <details>
            <summary>Ajuda do dicionário oficial</summary>
            <p>{spec.help}</p>
          </details>
        )}
      </label>
    );
  };
  const setGaia = (key, value) =>
    setData((d) => {
      const gaia = { ...d.gaia };
      if (value === "") delete gaia[key];
      else gaia[key] = value;
      return { ...d, gaia };
    });
  if (!schema)
    return <section>{error || "Carregando dicionário GAIA…"}</section>;
  return (
    <section className="nestor-editor">
      <h2>GAIA · Nestor</h2>
      <p>
        Prepare dragagem e despejo (dumping), áreas de intervenção e parâmetros
        sedimentares. Campos vazios opcionais são omitidos dos arquivos.
      </p>
      <p className="notice">
        Configuração para TELEMAC v8p5r0. Exporte os arquivos para executar pelo
        CLI: o executor web ainda não aceita GAIA. Os valores iniciais são
        ilustrativos e exigem parametrização do seu caso.
      </p>
      <p>
        <a
          href={`${schema.source}/-/tree/${schema.commit}/sources/nestor`}
          target="_blank"
          rel="noreferrer"
        >
          Código oficial Nestor
        </a>{" "}
        · revisão <code>{schema.commit.slice(0, 12)}</code>
      </p>
      {error && (
        <p role="alert" className="notice">
          {error}
        </p>
      )}
      {notice && (
        <p role="status" className="notice">
          {notice}
        </p>
      )}
      <fieldset disabled={busy}>
        <div className="toolbar">
          {upload("Importar ações Nestor", async (file) => {
            const form = new FormData();
            form.append("file", file);
            const r = await fetch("/api/nestor/import", {
              method: "POST",
              body: form,
            });
            const value = await r.json();
            if (!r.ok) throw Error(value.detail);
            setData((d) => ({ ...d, ...value }));
            setNotice(
              "Ações importadas. Confira as áreas e classes GAIA antes de exportar.",
            );
          })}
          <button
            onClick={() =>
              work(async () => {
                await save(
                  await request("/nestor/export", data),
                  "nestor_actions.dat",
                );
                setNotice("Ações validadas e exportadas.");
              })
            }
          >
            Exportar ações
          </button>
          <button
            onClick={() =>
              work(async () => {
                await save(
                  await request("/nestor/bundle", data),
                  "gaia_nestor.zip",
                );
                setNotice(
                  "Pacote exportado: GAIA, ações, polígonos, auxiliares necessários e instruções de acoplamento.",
                );
              })
            }
          >
            Exportar pacote GAIA + Nestor
          </button>
          <button
            className="secondary"
            onClick={() =>
              save(
                new Response(JSON.stringify(data, null, 2)),
                "gaia_nestor_project.json",
              )
            }
          >
            Salvar projeto do editor
          </button>
          {upload(
            "Abrir projeto do editor",
            async (file) => {
              const next = JSON.parse(await file.text());
              if (
                !Array.isArray(next.actions) ||
                !next.gaia ||
                typeof next.restart !== "boolean" ||
                ["polygons", "reference", "restart_file"].some(
                  (k) => typeof next[k] !== "string",
                )
              )
                throw Error("Projeto inválido");
              setData(next);
            },
            ".json",
          )}
        </div>
        <h3>1 · Sedimentos e arquivos GAIA</h3>
        <div className="toolbar">
          {upload(
            "Importar GAIA .cas",
            async (file) => {
              const form = new FormData();
              form.append("file", file);
              const r = await fetch("/api/cas/import", {
                method: "POST",
                body: form,
              });
              const value = await r.json();
              if (!r.ok) throw Error(value.detail);
              change("gaia", value);
            },
            ".cas",
          )}
          <button
            className="secondary"
            onClick={() => {
              if (hydro["GEOMETRY FILE"])
                setGaia("GEOMETRY FILE", hydro["GEOMETRY FILE"]);
            }}
          >
            Usar geometria do caso atual
          </button>
        </div>
        <p>
          Use a fronteira sedimentológica do GAIA. Listas de classes usam ponto
          e vírgula e a mesma ordem em todos os campos. Diâmetros em m,
          densidade em kg/m³ e velocidades de queda em m/s.
        </p>
        <div className="formgrid">
          {primary.filter((k) => schema.gaia[k]).map(gaiaField)}
        </div>
        <details>
          <summary>Todos os parâmetros GAIA · catálogo oficial</summary>
          <label>
            Buscar palavra-chave
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Ex.: SUSPENSION, NESTOR, POROSITY"
            />
          </label>
          <p>
            Os nomes dos arquivos Nestor são ajustados automaticamente no pacote
            exportado.
          </p>
          <div className="formgrid">
            {Object.keys(schema.gaia)
              .filter((k) => k.includes(search.toUpperCase()))
              .map(gaiaField)}
          </div>
        </details>
        <h3>2 · Ações de dragagem e despejo</h3>
        <p>
          Datas absolutas: aaaa.mm.dd-hh:mm:ss, coerentes com ORIGINAL DATE OF
          TIME / ORIGINAL HOUR OF TIME do TELEMAC. DigPlanar=TRUE e Reset_bottom
          não são compatíveis com esta configuração GAIA.
        </p>
        <label>
          Retomar estado Nestor
          <select
            value={String(data.restart)}
            onChange={(e) => change("restart", e.target.value === "true")}
          >
            <option value="false">FALSE · nova sequência</option>
            <option value="true">TRUE · requer arquivo de restart</option>
          </select>
        </label>
        <div className="toolbar">
          <select
            aria-label="Tipo de nova ação"
            value={kind}
            onChange={(e) => setKind(e.target.value)}
          >
            {Object.keys(schema.fields).map((k) => (
              <option key={k} value={k}>
                {titles[k]} · {k}
              </option>
            ))}
          </select>
          <button
            onClick={() =>
              change("actions", [...data.actions, { ActionType: kind }])
            }
          >
            Adicionar ação
          </button>
        </div>
        {!data.actions.length && (
          <p>Adicione uma ação ou importe um arquivo Nestor existente.</p>
        )}
        {data.actions.map((action, i) => (
          <article className="nestor-action" key={i}>
            <div className="toolbar">
              <h3>
                {i + 1} · {titles[action.ActionType] || action.ActionType}
              </h3>
              <button
                className="secondary"
                onClick={() =>
                  change(
                    "actions",
                    data.actions.filter((_, j) => i !== j),
                  )
                }
              >
                Remover ação {i + 1}
              </button>
            </div>
            {!schema.fields[action.ActionType] && (
              <p role="alert">
                Tipo não suportado no editor GAIA; ajuste o arquivo original.
              </p>
            )}
            <div className="formgrid">
              {(schema.fields[action.ActionType] || []).map((key) => (
                <label key={key}>
                  <span>
                    {schema.labels[key]}{" "}
                    {schema.required[action.ActionType].includes(key)
                      ? "*"
                      : ""}
                  </span>
                  {key === "ReferenceLevel" || key === "DumpPlanar" ? (
                    <select
                      value={action[key] || ""}
                      onChange={(e) => edit(i, key, e.target.value)}
                    >
                      <option value="">Não definido</option>
                      {(key === "ReferenceLevel"
                        ? schema.references
                        : ["FALSE", "TRUE"]
                      ).map((v) => (
                        <option key={v}>{v}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={schema.numeric.includes(key) ? "number" : "text"}
                      step="any"
                      value={
                        key === "GrainClass"
                          ? (action[key] || []).join(";")
                          : action[key] || ""
                      }
                      onChange={(e) =>
                        edit(
                          i,
                          key,
                          key === "GrainClass" && e.target.value !== ""
                            ? e.target.value.split(";")
                            : e.target.value,
                        )
                      }
                    />
                  )}
                  <small>{key}</small>
                </label>
              ))}
            </div>
          </article>
        ))}
        <h3>3 · Áreas e superfícies</h3>
        <p>
          Polígonos: NAME:100_area seguido de pares X Y (um por linha), no CRS
          da malha. Pelo menos três vértices distintos; use os três primeiros
          dígitos para associar FieldDig/FieldDump. Termine com END.
        </p>
        {upload("Importar polígonos", async (file) =>
          change("polygons", await file.text()),
        )}
        <label>
          Coordenadas dos polígonos
          <textarea
            rows="10"
            value={data.polygons}
            onChange={(e) => change("polygons", e.target.value)}
            placeholder={"NAME:100_dragagem\nX Y\n…\nEND"}
          />
        </label>
        <p>
          GRID/SECTIONS exigem a superfície de referência original. Em SECTIONS:
          xL yL zL xR yR zR km; em GRID, mantenha o formato oficial. O arquivo é
          preservado como texto, sem conversão ou validação completa.
          WATERLVL1–3 dependem de uma ação Save_water_level anterior.
        </p>
        {upload("Importar superfície de referência", async (file) =>
          change("reference", await file.text()),
        )}
        <label>
          Superfície de referência
          <textarea
            rows="7"
            value={data.reference}
            onChange={(e) => change("reference", e.target.value)}
          />
        </label>
        {data.restart && (
          <>
            {upload("Importar restart Nestor", async (file) =>
              change("restart_file", await file.text()),
            )}
            <label>
              Estado de restart · preservar formato gerado pelo solver
              <textarea
                rows="5"
                value={data.restart_file}
                onChange={(e) => change("restart_file", e.target.value)}
              />
            </label>
          </>
        )}
        <p>
          O pacote contém os arquivos de configuração; acrescente a malha,
          fronteiras e demais entradas do seu caso. A validação do editor não
          substitui uma execução de verificação no TELEMAC.
        </p>
      </fieldset>
    </section>
  );
}
