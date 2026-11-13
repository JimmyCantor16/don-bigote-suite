// El panel: armazon de aplicacion con secciones, tabla y hoja lateral.
//
// Por que asi, y no la pila de antes (formulario arriba, lista al final):
// quien entra viene a MIRAR sus registros, no a crear uno. La lista manda; el
// alta se pide en una hoja lateral cuando hace falta. Antes el primer registro
// empezaba en el pixel 1472, debajo de dos catalogos y siete campos.
import {
  listar, crear, actualizar, borrar, resumen,
  quienSoy, catalogos, crearEnCatalogo, borrarDeCatalogo,
} from "../api.js";
import { clearToken } from "../state.js";
import { dibujarCampos, leerCampos, limpiarCampos, escribirCampos, textoDeCampo } from "../campos.js";

const ICONOS = {
  lupa: 'M11 4a7 7 0 1 0 4.19 12.6l3.1 3.1 1.42-1.42-3.1-3.1A7 7 0 0 0 11 4Zm0 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10Z',
  editar: 'M4 16.5V20h3.5l9.4-9.4-3.5-3.5L4 16.5Zm15.7-9.6a1 1 0 0 0 0-1.4l-2.2-2.2a1 1 0 0 0-1.4 0l-1.7 1.7 3.5 3.5 1.8-1.6Z',
  borrar: 'M6 7h12v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7Zm3-3h6l1 2h3v2H5V6h3l1-2Z',
};

function icono(d, clase, titulo) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = clase;
  b.title = titulo;
  b.setAttribute("aria-label", titulo);
  b.innerHTML = `<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true"><path d="${d}"/></svg>`;
  return b;
}

/** Sin tildes y en minusculas: en espanol, "peluqueria" DEBE encontrar "Peluquería". */
function plano(s) {
  return String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

export function BoardView(onLogout) {
  const el = document.createElement("section");
  const A = window.__APP__;
  const CAMPOS = window.__CAMPOS__ || [];
  const CATS = window.__CATALOGOS__ || [];
  const plural = A.plural.toLowerCase();
  const singular = A.entidad.toLowerCase();

  el.className = "app";
  el.innerHTML = `
    <header class="barra">
      <div class="marca">
        <span class="logo" aria-hidden="true"></span>
        <h1></h1>
      </div>
      <span class="rol"></span>
      <button class="out ghost small" type="button">Salir</button>
    </header>
    <nav class="nav" aria-label="Secciones">
      <button class="nav-b" type="button" data-ir="lista" aria-current="page"></button>
      <button class="nav-b" type="button" data-ir="catalogos" hidden>Administración</button>
    </nav>
    <div class="lienzo">
      <section class="seccion sec-lista">
        <div class="resumen"></div>
        <div class="herramientas">
          <label class="buscar">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="${ICONOS.lupa}"/></svg>
            <input type="search" class="q" placeholder="Buscar…" aria-label="Buscar">
          </label>
          <span class="cuenta" role="status" aria-live="polite"></span>
          <span class="crece"></span>
          <button class="nuevo" type="button"></button>
        </div>
        <div class="tabla-caja"><table class="tabla"><thead></thead><tbody></tbody></table></div>
        <div class="vacio"><h3></h3><p></p><button class="vacio-nuevo" type="button"></button></div>
      </section>
      <section class="seccion sec-catalogos" hidden></section>
    </div>
    <p class="msg" role="status" aria-live="polite"></p>`;

  el.querySelector("h1").textContent = A.name;
  el.querySelector(".logo").textContent = (A.name.trim()[0] || "A").toUpperCase();
  el.querySelector('[data-ir="lista"]').textContent = A.plural;
  el.querySelector(".nuevo").textContent = "Añadir " + singular;
  el.querySelector(".vacio-nuevo").textContent = "Añadir " + singular;

  const q = el.querySelector(".q");
  const cuenta = el.querySelector(".cuenta");
  const thead = el.querySelector(".tabla thead");
  const tbody = el.querySelector(".tabla tbody");
  const cajaTabla = el.querySelector(".tabla-caja");
  const vacio = el.querySelector(".vacio");
  const cajaResumen = el.querySelector(".resumen");
  const cajaCat = el.querySelector(".sec-catalogos");
  const msg = el.querySelector(".msg");

  let yo = { es_admin: false };
  let items = {};
  let registros = [];
  let orden = { campo: null, asc: true };

  // --- Hoja lateral: crear y EDITAR --------------------------------------
  // El backend generado siempre supo actualizar (PUT /api/registros/<id>) y el
  // panel nunca se lo pedia: se podia crear y borrar, pero no corregir una
  // errata sin borrar y volver a escribirlo todo.
  const velo = document.createElement("div");
  velo.className = "velo";
  const hoja = document.createElement("aside");
  hoja.className = "hoja";
  hoja.setAttribute("role", "dialog");
  hoja.setAttribute("aria-modal", "true");
  hoja.innerHTML = `
    <div class="hoja-cab">
      <h2></h2>
      <button class="cerrar ghost small" type="button" aria-label="Cerrar">✕</button>
    </div>
    <div class="hoja-cuerpo"><form class="alta"></form></div>`;
  const form = hoja.querySelector("form.alta");
  const tituloHoja = hoja.querySelector(".hoja-cab h2");
  let editando = null;

  function abrirHoja(registro) {
    editando = registro || null;
    tituloHoja.textContent = registro ? "Editar " + singular : "Nuevo " + singular;
    limpiarCampos(form);
    if (registro) escribirCampos(form, registro);
    velo.classList.add("abierto");
    hoja.classList.add("abierta");
    const primero = form.querySelector("[data-campo]");
    if (primero) primero.focus();
  }
  function cerrarHoja() {
    velo.classList.remove("abierto");
    hoja.classList.remove("abierta");
    editando = null;
  }
  velo.onclick = cerrarHoja;
  hoja.querySelector(".cerrar").onclick = cerrarHoja;
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && hoja.classList.contains("abierta")) cerrarHoja();
  });
  el.querySelector(".nuevo").onclick = () => abrirHoja(null);
  el.querySelector(".vacio-nuevo").onclick = () => abrirHoja(null);

  // --- Secciones ----------------------------------------------------------
  function ir(seccion) {
    for (const b of el.querySelectorAll(".nav-b")) {
      const suya = b.dataset.ir === seccion;
      if (suya) b.setAttribute("aria-current", "page");
      else b.removeAttribute("aria-current");
    }
    el.querySelector(".sec-lista").hidden = seccion !== "lista";
    cajaCat.hidden = seccion !== "catalogos";
  }
  for (const b of el.querySelectorAll(".nav-b")) b.onclick = () => ir(b.dataset.ir);

  // --- Arranque -----------------------------------------------------------
  async function armar() {
    const rMe = await quienSoy();
    if (rMe.status === 401) { clearToken(); onLogout(); return; }
    if (rMe.ok) yo = await rMe.json();
    const rCat = await catalogos();
    if (rCat.ok) items = itemsPorNombre(await rCat.json());

    if (yo.es_admin) {
      const rol = el.querySelector(".rol");
      rol.textContent = "Administración";
      rol.className = "rol badge";
    }
    // La pestana de administracion solo existe si hay catalogos que administrar.
    el.querySelector('[data-ir="catalogos"]').hidden = !(yo.es_admin && CATS.length);

    form.innerHTML = "";
    dibujarCampos(form, items);
    const enviar = document.createElement("button");
    enviar.type = "submit";
    enviar.textContent = "Guardar";
    enviar.style.marginTop = "1.2rem";
    form.appendChild(enviar);

    pintarCabecera();
    pintarAdmin();
    await refrescar();
  }

  function itemsPorNombre(porSlug) {
    const salida = {};
    for (const def of CATS) {
      salida[def.nombre] = porSlug[def.slug] || [];
      salida[def.slug] = porSlug[def.slug] || [];
    }
    return salida;
  }

  // --- Tabla --------------------------------------------------------------
  function columnas() {
    const cols = CAMPOS.map((c) => ({ ...c, clave: c.nombre }));
    if (yo.es_admin) cols.unshift({ clave: "dueno", etiqueta: "De", tipo: "texto" });
    return cols;
  }

  function pintarCabecera() {
    const tr = document.createElement("tr");
    for (const c of columnas()) {
      const th = document.createElement("th");
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = c.etiqueta;
      b.onclick = () => {
        orden = { campo: c.clave, asc: orden.campo === c.clave ? !orden.asc : true };
        pintarFilas();
        pintarCabecera();
      };
      if (orden.campo === c.clave) {
        const f = document.createElement("span");
        f.textContent = orden.asc ? "▲" : "▼";
        b.appendChild(f);
        th.setAttribute("aria-sort", orden.asc ? "ascending" : "descending");
      }
      if (c.tipo === "entero" || c.tipo === "decimal") th.className = "num";
      th.appendChild(b);
      tr.appendChild(th);
    }
    const acc = document.createElement("th");
    acc.className = "acc";
    acc.innerHTML = '<span class="visualmente-oculto"></span>';
    tr.appendChild(acc);
    thead.innerHTML = "";
    thead.appendChild(tr);
  }

  function pintarFilas() {
    const busca = plano(q.value.trim());
    // El indice se calcula UNA vez por registro (al recibirlos), no en cada
    // pulsacion: con 200 registros y 9 columnas eran 1.800 normalizaciones por
    // tecla.
    let vistos = registros.filter((r) => !busca || r.__txt.includes(busca));

    if (orden.campo) {
      const dir = orden.asc ? 1 : -1;
      vistos = [...vistos].sort((a, b) => {
        const x = a[orden.campo], y = b[orden.campo];
        if (x === y) return 0;
        if (x === null || x === undefined || x === "") return 1;
        if (y === null || y === undefined || y === "") return -1;
        if (typeof x === "number" && typeof y === "number") return (x - y) * dir;
        return String(x).localeCompare(String(y), "es", { numeric: true }) * dir;
      });
    }

    tbody.innerHTML = "";
    for (const r of vistos) tbody.appendChild(fila(r));

    const hayRegistros = registros.length > 0;
    const hayVistos = vistos.length > 0;
    cajaTabla.hidden = !hayVistos;
    vacio.hidden = hayVistos;
    if (!hayVistos) {
      // Dos vacios distintos: "aun no hay nada" invita a crear; "no coincide"
      // invita a borrar el filtro. Confundirlos deja al usuario atascado.
      const h3 = vacio.querySelector("h3"), p = vacio.querySelector("p");
      const btn = vacio.querySelector(".vacio-nuevo");
      if (hayRegistros) {
        h3.textContent = "Sin coincidencias";
        p.textContent = 'Nada encuentra «' + q.value.trim() + '».';
        btn.textContent = "Quitar la búsqueda";
        btn.onclick = () => { q.value = ""; pintarFilas(); };
      } else {
        h3.textContent = "Aún no hay " + plural;
        p.textContent = "Añade el primero y aparecerá aquí.";
        btn.textContent = "Añadir " + singular;
        btn.onclick = () => abrirHoja(null);
      }
    }
    cuenta.textContent = busca
      ? vistos.length + " de " + registros.length
      : registros.length + " " + (registros.length === 1 ? singular : plural);
  }

  function fila(r) {
    const tr = document.createElement("tr");
    for (const c of columnas()) {
      const td = document.createElement("td");
      td.dataset.col = c.etiqueta;
      if (c.clave === "dueno") {
        if (r.dueno) {
          const s = document.createElement("span");
          s.className = "dueno";
          s.textContent = r.dueno;
          td.appendChild(s);
        }
      } else {
        td.textContent = textoDeCampo(c, r[c.clave]);
        if (c.tipo === "entero" || c.tipo === "decimal") td.className = "num";
      }
      tr.appendChild(td);
    }
    const acc = document.createElement("td");
    acc.className = "acc";
    acc.dataset.col = "";
    const bEditar = icono(ICONOS.editar, "icono", "Editar");
    bEditar.onclick = () => abrirHoja(r);
    const bBorrar = icono(ICONOS.borrar, "icono borrar", "Borrar");
    bBorrar.onclick = async () => {
      const res = await borrar(r.id);
      if (res.ok) refrescar();
    };
    acc.append(bEditar, bBorrar);
    tr.appendChild(acc);
    return tr;
  }

  // --- Administracion de catalogos ---------------------------------------
  function pintarAdmin() {
    cajaCat.innerHTML = "";
    if (!yo.es_admin || !CATS.length) return;
    for (const def of CATS) {
      const bloque = document.createElement("div");
      bloque.className = "cat";
      const titulo = document.createElement("h2");
      titulo.textContent = def.plural;
      bloque.appendChild(titulo);

      const ul = document.createElement("ul");
      ul.className = "cat-lista";
      for (const item of items[def.slug] || []) {
        const li = document.createElement("li");
        const texto = document.createElement("span");
        texto.textContent = def.campos
          .map((c) => item[c.nombre])
          .filter((v) => v !== null && v !== undefined && v !== "")
          .join(" · ");
        const quitar = icono(ICONOS.borrar, "icono borrar", "Quitar de " + def.plural.toLowerCase());
        quitar.onclick = async () => {
          const r = await borrarDeCatalogo(def.slug, item.id);
          if (r.ok) armar();
        };
        li.append(texto, quitar);
        ul.appendChild(li);
      }
      bloque.appendChild(ul);

      const alta = document.createElement("form");
      alta.className = "cat-alta";
      for (const c of def.campos) {
        const input = document.createElement("input");
        input.placeholder = c.etiqueta + (c.obligatorio ? " *" : "");
        input.dataset.campo = c.nombre;
        input.setAttribute("aria-label", c.etiqueta);
        if (c.tipo === "entero" || c.tipo === "decimal") {
          input.type = "number";
          input.step = c.tipo === "entero" ? "1" : "any";
        }
        alta.appendChild(input);
      }
      const anadir = document.createElement("button");
      anadir.type = "submit";
      anadir.className = "small";
      anadir.textContent = "Añadir";
      alta.appendChild(anadir);
      alta.onsubmit = async (ev) => {
        ev.preventDefault();
        const datos = {};
        for (const input of alta.querySelectorAll("[data-campo]")) {
          datos[input.dataset.campo] = input.type === "number"
            ? (input.value === "" ? null : Number(input.value))
            : input.value;
        }
        const r = await crearEnCatalogo(def.slug, datos);
        if (r.ok) { armar(); return; }
        const d = await r.json().catch(() => ({}));
        aviso(d.detail || "No se pudo añadir.", true);
      };
      bloque.appendChild(alta);
      cajaCat.appendChild(bloque);
    }
  }

  function aviso(texto, malo) {
    msg.textContent = texto;
    msg.className = malo ? "msg error" : "msg ok";
    // El mensaje de arriba se pierde de vista si estas al final de una lista
    // larga: la notificacion flotante confirma que la accion ocurrio.
    window.avisar?.(texto, malo ? "error" : "success");
  }

  async function refrescar() {
    const r = await listar();
    if (r.status === 401) { clearToken(); onLogout(); return; }
    registros = (await r.json()).map((reg) => ({
      ...reg,
      // Indice de busqueda precalculado, sobre TODO lo que se muestra: buscar
      // por algo que no se ve en ninguna columna seria desconcertante.
      __txt: plano(columnas().map((c) => textoDeCampo(c, reg[c.clave])).join(" ")),
    }));
    pintarFilas();

    const rs = await resumen();
    if (rs.ok) {
      const datos = await rs.json();
      cajaResumen.innerHTML = "";
      for (const clave of Object.keys(datos)) {
        const valor = datos[clave];
        const d = document.createElement("div");
        d.className = "dato";
        const v = document.createElement("div");
        v.className = "v";
        v.textContent = typeof valor === "number" ? valor.toLocaleString("es") : String(valor);
        const e = document.createElement("div");
        e.className = "e";
        e.textContent = clave;
        d.append(v, e);
        cajaResumen.appendChild(d);
      }
    }
  }

  q.oninput = () => pintarFilas();
  el.querySelector(".out").onclick = () => { clearToken(); onLogout(); };

  form.onsubmit = async (ev) => {
    ev.preventDefault();
    const datos = leerCampos(form);
    const r = editando ? await actualizar(editando.id, datos) : await crear(datos);
    if (r.ok) {
      cerrarHoja();
      aviso(editando ? "Cambio guardado." : "Añadido.", false);
      refrescar();
    } else {
      const d = await r.json().catch(() => ({}));
      // El motivo exacto del servidor: quien escribe debe saber que corregir.
      aviso(d.detail || "No se pudo guardar.", true);
    }
  };

  // El velo y la hoja viven FUERA del panel (position:fixed): dentro, el
  // `overflow:hidden` del marco los recortaria.
  document.body.append(velo, hoja);
  el.addEventListener("DOMNodeRemovedFromDocument", () => { velo.remove(); hoja.remove(); });

  armar();
  return el;
}
