// Estado mínimo: el token de sesión, guardado en el navegador.
let token = localStorage.getItem("token") || "";

export function getToken() { return token; }
export function setToken(t) { token = t; localStorage.setItem("token", t); }
export function clearToken() { token = ""; localStorage.removeItem("token"); }
export function isLogged() { return Boolean(token); }
