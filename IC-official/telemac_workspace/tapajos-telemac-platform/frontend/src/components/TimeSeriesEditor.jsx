import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
export default function TimeSeriesEditor({ qsl, onChange, onError }) {
  const [col, setCol] = useState(1),
    [page, setPage] = useState(0),
    [drag, setDrag] = useState(null);
  useEffect(() => {
    const release = () => setDrag(null);
    window.addEventListener("pointerup", release);
    return () => window.removeEventListener("pointerup", release);
  }, []);
  if (!qsl) return <p>Importe um arquivo .qsl para editar as séries.</p>;
  const c = Math.min(col, qsl.columns.length - 1),
    rows = qsl.rows,
    lo = Math.min(...rows.map((r) => r[c])),
    hi = Math.max(...rows.map((r) => r[c])),
    stride = Math.max(1, Math.ceil(rows.length / 600));
  const data = rows
    .map((r, i) => ({ t: r[0], v: r[c], index: i }))
    .filter((_, i) => i % stride === 0 || i === rows.length - 1);
  const update = (i, j, v) =>
    onChange({
      ...qsl,
      rows: rows.map((r, k) =>
        k === i ? r.map((x, l) => (l === j ? v : x)) : r,
      ),
    });
  const csv = async (file) => {
    try {
      const lines = (await file.text()).trim().split(/\r?\n/),
        sep = lines[0].includes(";") ? ";" : ",";
      const headers = lines.shift().toLowerCase().split(sep);
      const di = headers.indexOf("data"),
        ti = headers.indexOf("hora"),
        vi = headers.findIndex((h) =>
          ["vazao", "vazão", "valor", "q"].includes(h.trim()),
        );
      if (di < 0 || vi < 0)
        throw Error(
          "CSV esperado: data,hora,vazao. Para cota use conversor Python com unidade e datum explícitos.",
        );
      const out = lines.map((l) => {
        const a = l.split(sep);
        let date = a[di];
        if (date.includes("/")) date = date.split("/").reverse().join("-");
        return [
          Date.parse(date + "T" + (ti >= 0 ? a[ti] : "00:00:00") + "Z") / 1000,
          Number(a[vi].replace(",", ".")),
        ];
      });
      const t0 = out[0][0];
      out.forEach((r) => (r[0] -= t0));
      if (
        out.some(
          (r, i) => !r.every(Number.isFinite) || (i && r[0] <= out[i - 1][0]),
        )
      )
        throw Error("Datas inválidas, duplicadas ou fora de ordem");
      onChange({ columns: ["T", "Q(1)"], units: ["s", "m3/s"], rows: out });
      setPage(0);
    } catch (e) {
      onError(e.message);
    }
  };
  return (
    <>
      <div className="toolbar">
        <select
          aria-label="Série"
          value={c}
          onChange={(e) => setCol(+e.target.value)}
        >
          {qsl.columns.slice(1).map((x, i) => (
            <option value={i + 1} key={i}>
              {x} [{qsl.units[i + 1]}]
            </option>
          ))}
        </select>
        <label className="button secondary">
          Importar CSV de vazão
          <input
            type="file"
            accept=".csv"
            onChange={(e) => e.target.files[0] && csv(e.target.files[0])}
          />
        </label>
        <span>
          {rows.length.toLocaleString()} pontos · {rows.at(-1)[0]} s
        </span>
      </div>
      <div style={{ height: 320 }} onPointerUp={() => setDrag(null)}>
        <ResponsiveContainer>
          <LineChart
            data={data}
            margin={{ top: 12, right: 20, bottom: 20, left: 20 }}
            onMouseDown={(e) => {
              if (e?.activeTooltipIndex != null)
                setDrag({
                  index: data[+e.activeTooltipIndex]?.index,
                  lo,
                  hi: hi === lo ? lo + 1 : hi,
                });
            }}
            onMouseMove={(e) => {
              if (drag !== null && e?.chartY != null) {
                const value =
                  drag.hi -
                  Math.max(0, Math.min(1, (e.chartY - 12) / 258)) *
                    (drag.hi - drag.lo);
                update(drag.index, c, +value.toFixed(4));
              }
            }}
            onMouseUp={() => setDrag(null)}
          >
            <CartesianGrid stroke="#e3eae5" vertical={false} />
            <XAxis
              dataKey="t"
              type="number"
              domain={["dataMin", "dataMax"]}
              label={{ value: "Tempo [s]", position: "bottom" }}
            />
            <YAxis
              domain={drag ? [drag.lo, drag.hi] : ["auto", "auto"]}
              allowDataOverflow={!!drag}
            />
            <Tooltip />
            <Line
              dataKey="v"
              stroke="#28776c"
              strokeWidth={2}
              dot={data.length < 100}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p>
        Arraste um ponto da curva na vertical ou edite os valores abaixo. A
        exportação rejeita tempos duplicados, lacunas vazias e valores
        inválidos.
      </p>
      <div className="tablewrap">
        <table>
          <thead>
            <tr>
              {qsl.columns.map((x, i) => (
                <th key={x}>
                  {x} [{qsl.units[i]}]
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(page * 20, page * 20 + 20).map((r, i) => (
              <tr key={i}>
                {r.map((v, j) => (
                  <td key={j}>
                    <input
                      type="number"
                      aria-label={`Ponto ${page * 20 + i + 1} ${qsl.columns[j]}`}
                      value={v}
                      onChange={(e) =>
                        update(
                          page * 20 + i,
                          j,
                          e.target.value === "" ? NaN : +e.target.value,
                        )
                      }
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="toolbar">
        <button
          className="secondary"
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
        >
          Anterior
        </button>
        <span>
          Página {page + 1} / {Math.ceil(rows.length / 20)}
        </span>
        <button
          className="secondary"
          disabled={(page + 1) * 20 >= rows.length}
          onClick={() => setPage(page + 1)}
        >
          Próxima
        </button>
      </div>
    </>
  );
}
