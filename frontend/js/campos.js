// Construye y lee el formulario a partir de los campos del dominio.
// Cada tipo tiene su control: un número no se pide con una caja de texto.

export function dibujarCampos(contenedor, itemsCatalogos) {
  itemsCatalogos = itemsCatalogos || {};
  for (const c of window.__CAMPOS__) {
    const id = "f_" + c.nombre;
    const label = document.createElement("label");
    label.setAttribute("for", id);
    label.textContent = c.etiqueta;
    if (c.obligatorio) {
      const req = document.createElement("span");
      req.className = "req";
      req.textContent = " *";
      label.appendChild(req);
    }
    contenedor.appendChild(label);

    let control;
    if (c.tipo === "relacion") {
      // Un desplegable con los ítems REALES del catálogo (los barberos que la
      // dueña dio de alta), no una caja de texto libre.
      control = document.createElement("select");
      const vacia = document.createElement("option");
      vacia.value = "";
      vacia.textContent = "Elige...";
      control.appendChild(vacia);
      const def = (window.__CATALOGOS__ || []).find((k) => k.slug === c.catalogo) || {};
      const visible = def.visible || "nombre";
      for (const item of itemsCatalogos[c.catalogo] || []) {
        const op = document.createElement("option");
        op.value = String(item[visible] ?? "");
        op.textContent = String(item[visible] ?? "");
        control.appendChild(op);
      }
    } else if (c.tipo === "opcion") {
      control = document.createElement("select");
      const vacia = document.createElement("option");
      vacia.value = "";
      vacia.textContent = "Elige...";
      control.appendChild(vacia);
      for (const o of c.opciones) {
        const op = document.createElement("option");
        op.value = o;
        op.textContent = o;
        control.appendChild(op);
      }
    } else if (c.tipo === "texto_largo") {
      control = document.createElement("textarea");
    } else {
      control = document.createElement("input");
      if (c.tipo === "entero") { control.type = "number"; control.step = "1"; }
      else if (c.tipo === "decimal") { control.type = "number"; control.step = "any"; }
      else if (c.tipo === "fecha") { control.type = "date"; }
      else if (c.tipo === "booleano") { control.type = "checkbox"; }
      else { control.type = "text"; }
      if (c.minimo !== null && c.minimo !== undefined) control.min = c.minimo;
      if (c.maximo !== null && c.maximo !== undefined) control.max = c.maximo;
    }
    control.id = id;
    control.dataset.campo = c.nombre;
    control.dataset.tipo = c.tipo;
    if (c.obligatorio && c.tipo !== "booleano") control.required = true;
    contenedor.appendChild(control);

    if (c.ayuda) {
      const p = document.createElement("p");
      p.className = "ayuda";
      p.textContent = c.ayuda;
      contenedor.appendChild(p);
    }
  }
}

/** Recoge lo escrito, ya convertido al tipo que espera el servidor. */
export function leerCampos(contenedor) {
  const datos = {};
  for (const el of contenedor.querySelectorAll("[data-campo]")) {
    const tipo = el.dataset.tipo;
    if (tipo === "booleano") datos[el.dataset.campo] = el.checked;
    else if (tipo === "entero" || tipo === "decimal")
      datos[el.dataset.campo] = el.value === "" ? null : Number(el.value);
    else datos[el.dataset.campo] = el.value;
  }
  return datos;
}

export function limpiarCampos(contenedor) {
  for (const el of contenedor.querySelectorAll("[data-campo]")) {
    if (el.dataset.tipo === "booleano") el.checked = false;
    else el.value = "";
  }
}

/** Vuelca un registro EN el formulario. Es lo que hace posible editar. */
export function escribirCampos(contenedor, registro) {
  for (const el of contenedor.querySelectorAll("[data-campo]")) {
    const valor = registro[el.dataset.campo];
    if (el.dataset.tipo === "booleano") el.checked = Boolean(valor);
    else el.value = valor === null || valor === undefined ? "" : String(valor);
  }
}

/**
 * Como se MUESTRA el valor de un campo.
 *
 * Vive aqui y no en la tabla para que la celda, la ficha del movil y el indice
 * de busqueda digan exactamente lo mismo: si la tabla mostrara "Si" y el indice
 * guardara "true", buscar "si" no encontraria la fila que lo dice en pantalla.
 */
export function textoDeCampo(campo, valor) {
  if (valor === null || valor === undefined || valor === "") return "";
  if (campo.tipo === "booleano") return valor ? "Sí" : "No";
  if (campo.tipo === "entero" || campo.tipo === "decimal") {
    return Number(valor).toLocaleString("es");
  }
  return String(valor);
}

/** Pinta un registro mostrando cada campo con su etiqueta. */
export function pintarRegistro(r) {
  const datos = document.createElement("div");
  datos.className = "datos";
  for (const c of window.__CAMPOS__) {
    const valor = r[c.nombre];
    if (valor === null || valor === undefined || valor === "") continue;
    const par = document.createElement("p");
    par.className = "par";
    const et = document.createElement("b");
    et.textContent = c.etiqueta;
    const v = document.createElement("span");
    if (c.tipo === "booleano") v.textContent = valor ? "Si" : "No";
    else v.textContent = String(valor);
    if (c.tipo === "entero" || c.tipo === "decimal") v.className = "num";
    par.append(et, v);
    datos.appendChild(par);
  }
  return datos;
}
