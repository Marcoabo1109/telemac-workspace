import React, { useEffect, useRef, useState } from "react";

const colors = ["#27aecc", "#ed9f45", "#c36da2"];
function RiverMap({ data, frame, material }) {
  const canvas = useRef(null),
    [probe, setProbe] = useState(null);
  const transform = useRef(null);
  useEffect(() => {
    const c = canvas.current;
    const draw = () => {
      const width = c.clientWidth,
        height = 360,
        ratio = window.devicePixelRatio || 1;
      c.width = width * ratio;
      c.height = height * ratio;
      const ctx = c.getContext("2d");
      ctx.scale(ratio, ratio);
      ctx.fillStyle = "#0d2630";
      ctx.fillRect(0, 0, width, height);
      const xmin = Math.min(...data.x),
        xmax = Math.max(...data.x),
        ymin = Math.min(...data.y),
        ymax = Math.max(...data.y);
      const scale = Math.min(
        (width - 50) / (xmax - xmin),
        (height - 50) / (ymax - ymin),
      );
      const ox = (width - (xmax - xmin) * scale) / 2,
        oy = (height - (ymax - ymin) * scale) / 2;
      const px = (x) => ox + (x - xmin) * scale,
        py = (y) => height - oy - (y - ymin) * scale;
      transform.current = { px, py };
      const values = data.concentrations[frame][material];
      data.triangles.forEach((t) => {
        const value = Math.max(
          0,
          Math.min(1, t.reduce((s, i) => s + values[i], 0) / 3),
        );
        ctx.fillStyle = `hsl(${210 - 170 * value} 82% ${18 + 45 * value}%)`;
        ctx.beginPath();
        t.forEach((i, j) =>
          j
            ? ctx.lineTo(px(data.x[i]), py(data.y[i]))
            : ctx.moveTo(px(data.x[i]), py(data.y[i])),
        );
        ctx.closePath();
        ctx.fill();
      });
      const [sx, sy] = data.metadata.release_xy_m;
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(px(sx), py(sy), 6, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = "#dbe9e7";
      ctx.font = "11px system-ui";
      ctx.fillText("N ↑", width - 40, 22);
      ctx.fillText("Pulso inicial ○", 12, 22);
      ctx.fillRect(15, height - 20, 500 * scale, 2);
      ctx.fillText("500 m", 15, height - 26);
    };
    const observer = new ResizeObserver(draw);
    observer.observe(c);
    draw();
    return () => observer.disconnect();
  }, [data, frame, material]);
  const inspect = (e) => {
    const rect = canvas.current.getBoundingClientRect();
    const x = e.clientX - rect.left,
      y = e.clientY - rect.top;
    let best = Infinity,
      index = 0;
    data.x.forEach((v, i) => {
      const d =
        (transform.current.px(v) - x) ** 2 +
        (transform.current.py(data.y[i]) - y) ** 2;
      if (d < best) {
        best = d;
        index = i;
      }
    });
    setProbe(best < 900 ? index : null);
  };
  return (
    <div>
      <canvas
        ref={canvas}
        className="poc-map"
        aria-label={`Dispersão de ${data.materials[material].name}`}
        onPointerMove={inspect}
        onPointerLeave={() => setProbe(null)}
      />
      <div className="poc-probe">
        {probe === null
          ? "Passe o cursor sobre o rio para consultar C/C₀."
          : `Nó ${probe + 1} · C/C₀ = ${data.concentrations[frame][material][probe].toFixed(4)}`}
      </div>
    </div>
  );
}

export default function DispersionPoC() {
  const [data, setData] = useState(null),
    [error, setError] = useState(""),
    [frame, setFrame] = useState(0),
    [playing, setPlaying] = useState(false),
    [compare, setCompare] = useState(true),
    [material, setMaterial] = useState(0),
    [speed, setSpeed] = useState(250);
  const load = () => {
    setError("");
    fetch("/api/poc/materials")
      .then(async (r) => {
        if (!r.ok)
          throw Error(
            "Resultados indisponíveis. Execute o PoC conforme a documentação.",
          );
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  };
  useEffect(load, []);
  useEffect(() => {
    if (!playing || !data) return;
    const timer = setInterval(
      () =>
        setFrame((f) => {
          if (f >= data.times.length - 1) {
            setPlaying(false);
            return f;
          }
          return f + 1;
        }),
      speed,
    );
    return () => clearInterval(timer);
  }, [playing, data, speed]);
  if (error)
    return (
      <div role="alert" className="error">
        {error} <button onClick={load}>Tentar novamente</button>
      </div>
    );
  if (!data)
    return (
      <div role="status" className="empty">
        Carregando resultados TELEMAC…
      </div>
    );
  const initial = data.inventory_normalized_m3[0];
  const shown = compare ? [0, 1, 2] : [material];
  return (
    <section className="poc">
      <div className="poc-intro">
        <div>
          <span className="eyebrow">
            POC · OPENTELEMAC 2D · RESULTADOS EXECUTADOS
          </span>
          <h2>Um rio. Três destinos.</h2>
          <p>
            Tapajós, Itaituba · pulso inicial de material transportado ao longo
            de um trecho de 3,47 km.
          </p>
        </div>
        <span className="poc-badge">Exploratório · sem calibração</span>
      </div>
      <div className="poc-controls">
        <button
          onClick={() => {
            if (frame === data.times.length - 1) setFrame(0);
            setPlaying(!playing);
          }}
        >
          {playing ? "❚❚ Pausar" : "▶ Reproduzir"}
        </button>
        <button
          className="secondary"
          onClick={() => {
            setPlaying(false);
            setFrame(0);
          }}
        >
          Reiniciar
        </button>
        <strong>
          {(data.times[frame] / 60).toFixed(0).padStart(2, "0")} / 60 min
        </strong>
        <input
          aria-label="Instante da dispersão"
          type="range"
          min="0"
          max={data.times.length - 1}
          value={frame}
          onChange={(e) => {
            setPlaying(false);
            setFrame(+e.target.value);
          }}
        />
        <select
          aria-label="Velocidade da animação"
          value={speed}
          onChange={(e) => setSpeed(+e.target.value)}
        >
          <option value={500}>2 quadros/s</option>
          <option value={250}>4 quadros/s</option>
          <option value={125}>8 quadros/s</option>
        </select>
      </div>
      <div className="poc-options">
        <label>
          <input
            type="checkbox"
            checked={compare}
            onChange={(e) => setCompare(e.target.checked)}
          />{" "}
          Comparar os três materiais
        </label>
        {!compare && (
          <select
            aria-label="Material exibido"
            value={material}
            onChange={(e) => setMaterial(+e.target.value)}
          >
            {data.materials.map((m, i) => (
              <option key={m.id} value={i}>
                {m.name}
              </option>
            ))}
          </select>
        )}
        <span>Escala fixa e comum · concentração normalizada C/C₀</span>
      </div>
      <div className={`poc-maps ${compare ? "comparison" : ""}`}>
        {shown.map((i) => (
          <article key={i}>
            <div className="poc-card-title">
              <i style={{ background: colors[i] }} />
              <h3>{data.materials[i].name}</h3>
            </div>
            <p>{data.materials[i].description}</p>
            <RiverMap data={data} frame={frame} material={i} />
            <div className="poc-card-stat">
              <strong>
                {(
                  (100 * data.inventory_normalized_m3[frame][i]) /
                  initial[i]
                ).toFixed(1)}
                %
              </strong>
              <span>do inventário inicial ainda na água do trecho</span>
            </div>
          </article>
        ))}
      </div>
      <div className="poc-scale">
        <span>0</span>
        <div />
        <span>1 C/C₀</span>
      </div>
      <div className="poc-bottom">
        <article>
          <h3>Material presente no trecho</h3>
          <p>
            Inventário relativo ao inicial. Saída pela fronteira também reduz o
            inventário; redução não significa apenas reação.
          </p>
          <svg
            viewBox="0 0 600 160"
            role="img"
            aria-label="Evolução do inventário dos três materiais"
          >
            <path d="M35 10V135H585" fill="none" stroke="#b8c9c4" />
            <text x="0" y="18" fontSize="11">
              100%
            </text>
            <text x="15" y="138" fontSize="11">
              0%
            </text>
            <text x="35" y="155" fontSize="11">
              0 min
            </text>
            <text x="545" y="155" fontSize="11">
              60 min
            </text>
            {[0, 1, 2].map((i) => (
              <polyline
                key={i}
                fill="none"
                stroke={colors[i]}
                strokeWidth="2.5"
                points={data.times
                  .map(
                    (t, j) =>
                      `${35 + (550 * t) / 3600},${135 - (120 * data.inventory_normalized_m3[j][i]) / initial[i]}`,
                  )
                  .join(" ")}
              />
            ))}
            <line
              x1={35 + (550 * data.times[frame]) / 3600}
              x2={35 + (550 * data.times[frame]) / 3600}
              y1="10"
              y2="135"
              stroke="#42615a"
              strokeDasharray="4 3"
            />
          </svg>
        </article>
        <article>
          <h3>O que este experimento representa</h3>
          <p>
            Mesmo pulso, escoamento e difusividade para os três materiais.
            Poluente: perda de primeira ordem. Sedimento: retirada da suspensão
            por deposição, sem erosão ou atualização do leito.
          </p>
          <p>
            <strong>Dados públicos:</strong> eixo do rio © OpenStreetMap;
            estatística de nível SGB. Séries diárias ANA estão disponíveis no
            projeto.
          </p>
          <p>
            <strong>Hipóteses:</strong> vazão 6.000 m³/s, largura 1.200 m, fundo
            esquemático, datum local e propriedades dos materiais. Este PoC não
            usa as séries ANA como contorno nem estima concentrações ambientais
            reais.
          </p>
        </article>
      </div>
      <details>
        <summary>Fonte, parâmetros e reprodução</summary>
        <p>
          <a href={data.metadata.solver_git} target="_blank" rel="noreferrer">
            Repositório Git oficial TELEMAC-MASCARET
          </a>{" "}
          · {data.metadata.solver_version} · revisão{" "}
          <code>{data.metadata.solver_commit.slice(0, 12)}</code>
        </p>
        <p>
          {data.metadata.nodes} nós · {data.metadata.triangles} triângulos · Δt
          = 1 s · 61 instantes · EPSG:32721. Convergência espacial do traçador
          ainda pendente.
        </p>
        <p>
          <a
            href={data.metadata.data.axis.url}
            target="_blank"
            rel="noreferrer"
          >
            Eixo público OpenStreetMap
          </a>{" "}
          ·{" "}
          <a
            href="https://www.snirh.gov.br/hidroweb/"
            target="_blank"
            rel="noreferrer"
          >
            ANA HidroWeb
          </a>
        </p>
        <a className="button secondary" href="/api/poc/materials/download">
          Baixar resultados e metadados JSON
        </a>
        <p>
          Reprodução no ambiente TELEMAC:{" "}
          <code>python -m scripts.materials_poc</code>. Fontes Fortran e caso
          disponíveis em <code>models/tapajos_materials</code>.
        </p>
      </details>
    </section>
  );
}
