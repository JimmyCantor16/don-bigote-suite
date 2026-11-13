// Cliente de API. Rutas relativas: sirven igual en local y en producción.
import { getToken } from "./state.js";

async function req(path, opts = {}) {
  const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;
  return fetch(path, Object.assign({}, opts, { headers }));
}

export async function register(username, password) {
  return req("api/register", { method: "POST", body: JSON.stringify({ username, password }) });
}

export async function login(username, password) {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);
  return fetch("api/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

export async function listar() { return req("api/registros"); }
export async function crear(datos) { return req("api/registros", { method: "POST", body: JSON.stringify(datos) }); }
// El backend siempre supo actualizar; hasta ahora nadie se lo pedia, asi que
// una errata obligaba a borrar el registro y volver a escribirlo entero.
export async function actualizar(id, datos) {
  return req("api/registros/" + id, { method: "PUT", body: JSON.stringify(datos) });
}
export async function borrar(id) { return req("api/registros/" + id, { method: "DELETE" }); }
export async function resumen() { return req("api/resumen"); }

// Quién soy (decide si se muestra el panel de administración) y los catálogos
// del negocio (alimentan los desplegables y el panel del admin).
export async function quienSoy() { return req("api/me"); }
export async function catalogos() { return req("api/catalogos"); }
export async function crearEnCatalogo(slug, datos) {
  return req("api/catalogos/" + slug, { method: "POST", body: JSON.stringify(datos) });
}
export async function borrarDeCatalogo(slug, id) {
  return req("api/catalogos/" + slug + "/" + id, { method: "DELETE" });
}
