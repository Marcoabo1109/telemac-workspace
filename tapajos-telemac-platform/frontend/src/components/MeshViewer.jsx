import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
export default function MeshViewer({
  mesh,
  edits = {},
  onEdit,
  cli = [],
  editable = false,
}) {
  const host = useRef(),
    [selected, setSelected] = useState(null),
    [field, setField] = useState(0),
    [min, setMin] = useState(""),
    [max, setMax] = useState(""),
    [z, setZ] = useState(""),
    [vectors, setVectors] = useState(false);
  useEffect(() => {
    setSelected(null);
    setField(0);
    setMin("");
    setMax("");
  }, [mesh?.title, mesh?.x.length]);
  useEffect(() => {
    if (!mesh || !host.current) return;
    const h = host.current,
      w = h.clientWidth,
      height = 430,
      scene = new THREE.Scene();
    scene.background = new THREE.Color("#f0f5f2");
    const r = new THREE.WebGLRenderer({ antialias: true });
    r.setSize(w, height);
    r.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    h.appendChild(r.domElement);
    const xmin = Math.min(...mesh.x),
      xmax = Math.max(...mesh.x),
      ymin = Math.min(...mesh.y),
      ymax = Math.max(...mesh.y),
      cx = (xmin + xmax) / 2,
      cy = (ymin + ymax) / 2,
      span = Math.max(xmax - xmin, ((ymax - ymin) * w) / height) * 1.14 || 1;
    const camera = new THREE.OrthographicCamera(
      -span / 2,
      span / 2,
      (span * height) / w / 2,
      (-span * height) / w / 2,
      0.1,
      100,
    );
    camera.position.z = 10;
    let values = mesh.values[field] || mesh.x.map(() => 0);
    if (
      ["BOTTOM", "FOND"].includes(
        mesh.variables[field]?.name.trim().toUpperCase(),
      )
    )
      values = values.map((v, i) => edits[i] ?? v);
    const lo = min === "" ? Math.min(...values) : +min,
      hi = max === "" ? Math.max(...values) : +max,
      positions = [],
      colors = [];
    mesh.triangles.forEach((t) =>
      t.forEach((i) => {
        positions.push(mesh.x[i] - cx, mesh.y[i] - cy, 0);
        const f = Math.max(0, Math.min(1, (values[i] - lo) / (hi - lo || 1)));
        const c = new THREE.Color().setHSL(
          0.52 - 0.35 * f,
          0.36,
          0.3 + 0.36 * f,
        );
        colors.push(c.r, c.g, c.b);
      }),
    );
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    const material = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
    });
    scene.add(new THREE.Mesh(g, material));
    const edges = new THREE.LineSegments(
      new THREE.WireframeGeometry(g),
      new THREE.LineBasicMaterial({
        color: "#214e4b",
        transparent: true,
        opacity: 0.16,
      }),
    );
    edges.position.z = 0.01;
    scene.add(edges);
    const boundary = [];
    const bc = [];
    cli.forEach((row) => {
      const i = row[11] - 1;
      if (i < 0 || i >= mesh.x.length) return;
      boundary.push(mesh.x[i] - cx, mesh.y[i] - cy, 0.03);
      const c = new THREE.Color(
        row[0] === 5 ? "#db833d" : row[1] === 5 ? "#2468bd" : "#496860",
      );
      bc.push(c.r, c.g, c.b);
    });
    const bg = new THREE.BufferGeometry();
    bg.setAttribute("position", new THREE.Float32BufferAttribute(boundary, 3));
    bg.setAttribute("color", new THREE.Float32BufferAttribute(bc, 3));
    scene.add(
      new THREE.Points(
        bg,
        new THREE.PointsMaterial({ vertexColors: true, size: 3 }),
      ),
    );
    if (vectors) {
      const ui = mesh.variables.findIndex((v) =>
          ["VELOCITY U", "VITESSE U"].includes(v.name.trim()),
        ),
        vi = mesh.variables.findIndex((v) =>
          ["VELOCITY V", "VITESSE V"].includes(v.name.trim()),
        );
      if (ui >= 0 && vi >= 0) {
        const u = mesh.values[ui],
          v = mesh.values[vi],
          scale =
            span /
            40 /
            (Math.max(...u.map((x, i) => Math.hypot(x, v[i]))) || 1),
          lines = [];
        for (
          let i = 0;
          i < u.length;
          i += Math.max(1, Math.floor(u.length / 180))
        ) {
          const x = mesh.x[i] - cx,
            y = mesh.y[i] - cy,
            dx = u[i] * scale,
            dy = v[i] * scale;
          lines.push(
            x,
            y,
            0.04,
            x + dx,
            y + dy,
            0.04,
            x + dx,
            y + dy,
            0.04,
            x + 0.7 * dx + 0.15 * dy,
            y + 0.7 * dy - 0.15 * dx,
            0.04,
            x + dx,
            y + dy,
            0.04,
            x + 0.7 * dx - 0.15 * dy,
            y + 0.7 * dy + 0.15 * dx,
            0.04,
          );
        }
        const vg = new THREE.BufferGeometry();
        vg.setAttribute("position", new THREE.Float32BufferAttribute(lines, 3));
        scene.add(
          new THREE.LineSegments(
            vg,
            new THREE.LineBasicMaterial({ color: "#072c3c" }),
          ),
        );
      }
    }
    const render = () => r.render(scene, camera);
    render();
    let down = null,
      moved = false;
    const wheel = (e) => {
      e.preventDefault();
      camera.zoom = Math.max(
        0.3,
        Math.min(30, camera.zoom * Math.exp(-e.deltaY * 0.001)),
      );
      camera.updateProjectionMatrix();
      render();
    };
    const pd = (e) => {
      down = [e.offsetX, e.offsetY];
      moved = false;
      r.domElement.setPointerCapture(e.pointerId);
    };
    const pm = (e) => {
      if (!down) return;
      const dx = e.offsetX - down[0],
        dy = e.offsetY - down[1];
      if (Math.abs(dx) + Math.abs(dy) > 2) moved = true;
      camera.position.x -= (dx * span) / w / camera.zoom;
      camera.position.y += (dy * span) / w / camera.zoom;
      down = [e.offsetX, e.offsetY];
      render();
    };
    const pu = (e) => {
      down = null;
      if (moved || !editable) return;
      const p = new THREE.Vector3(
        (e.offsetX / w) * 2 - 1,
        1 - (e.offsetY / height) * 2,
        0,
      ).unproject(camera);
      let nearest = 0,
        d = Infinity;
      mesh.x.forEach((x, i) => {
        const dd = (x - cx - p.x) ** 2 + (mesh.y[i] - cy - p.y) ** 2;
        if (dd < d) {
          d = dd;
          nearest = i;
        }
      });
      setSelected(nearest);
      const b = mesh.variables.findIndex((v) =>
        ["BOTTOM", "FOND"].includes(v.name.trim()),
      );
      setZ(edits[nearest] ?? mesh.values[b]?.[nearest] ?? "");
    };
    r.domElement.addEventListener("wheel", wheel, { passive: false });
    r.domElement.addEventListener("pointerdown", pd);
    r.domElement.addEventListener("pointermove", pm);
    r.domElement.addEventListener("pointerup", pu);
    return () => {
      r.domElement.removeEventListener("wheel", wheel);
      r.domElement.remove();
      scene.traverse((o) => {
        o.geometry?.dispose();
        if (o.material) o.material.dispose();
      });
      r.dispose();
    };
  }, [mesh, edits, field, min, max, cli, vectors, editable]);
  if (!mesh)
    return <div className="empty">Importe uma malha SERAFIN para começar.</div>;
  return (
    <div>
      <div className="meshcontrols">
        <select
          aria-label="Campo exibido"
          value={field}
          onChange={(e) => setField(+e.target.value)}
        >
          {mesh.variables.map((v, i) => (
            <option value={i} key={i}>
              {v.name} {v.unit}
            </option>
          ))}
        </select>
        <input
          aria-label="Mínimo da escala"
          placeholder="Mín. automático"
          value={min}
          type="number"
          onChange={(e) => setMin(e.target.value)}
        />
        <input
          aria-label="Máximo da escala"
          placeholder="Máx. automático"
          value={max}
          type="number"
          onChange={(e) => setMax(e.target.value)}
        />
        <label>
          <input
            type="checkbox"
            checked={vectors}
            onChange={(e) => setVectors(e.target.checked)}
          />{" "}
          Velocidades
        </label>
      </div>
      <div ref={host} className="meshcanvas" />
      <div className="meshlegend">
        <span>
          Arraste para mover · role para ampliar
          {editable ? " · clique para selecionar nó" : ""}
        </span>
        <span className="gradient" /> Baixo → Alto
      </div>
      {selected !== null && (
        <div className="toolbar">
          <span>Nó {selected + 1} · z_b [m]</span>
          <input
            aria-label="Cota do nó"
            type="number"
            value={z}
            onChange={(e) => setZ(e.target.value)}
          />
          <button
            onClick={() => {
              if (z !== "" && Number.isFinite(+z)) onEdit(selected, +z);
            }}
          >
            Aplicar cota
          </button>
        </div>
      )}
    </div>
  );
}
