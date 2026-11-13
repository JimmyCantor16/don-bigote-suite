// PANTALLA DE ENTRAR. El registro vive en su propia pantalla (registro.js).
import { login } from "../api.js";
import { setToken } from "../state.js";
import { reglas, campo, gobernar } from "../validacion.js";

export function LoginView(onLogged, irARegistro) {
  const el = document.createElement("section");
  el.className = "card";
  // Los campos van dentro de un <form> de verdad: así el Enter envía y los
  // gestores de contraseñas del navegador ofrecen guardar y autocompletar.
  el.innerHTML = `
    <h1></h1>
    <p class="sub">Entra con tu cuenta para continuar.</p>
    <form class="entrar" novalidate>
      <label for="u">Usuario</label>
      <input id="u" class="u" name="username" autocomplete="username" aria-describedby="u-err">
      <p class="u-error error-campo" id="u-err" role="alert"></p>
      <label for="p">Contraseña</label>
      <input id="p" class="p" name="password" type="password" autocomplete="current-password" aria-describedby="p-err">
      <p class="p-error error-campo" id="p-err" role="alert"></p>
      <div class="row">
        <button class="in" type="submit" disabled>Entrar</button>
      </div>
    </form>
    <p class="msg" role="status" aria-live="polite"></p>
    <p class="ayuda">¿No tienes cuenta?
      <a href="#/registro" class="ir-registro">Crea una aquí</a>.</p>
    <div class="mirar"></div>`;

  el.querySelector("h1").textContent = window.__APP__.name;

  const msg = el.querySelector(".msg");
  const boton = el.querySelector(".in");
  const cu = campo(el, "u", reglas.usuario, () => repintar());
  const cp = campo(el, "p", reglas.claveDeEntrada, () => repintar());
  const repintar = gobernar(boton, [cu, cp]);

  el.querySelector(".ir-registro").onclick = (e) => { e.preventDefault(); irARegistro(); };

  el.querySelector("form.entrar").onsubmit = async (e) => {
    e.preventDefault();
    if (cu.revisar() || cp.revisar()) return;
    boton.disabled = true;
    msg.textContent = "Entrando…";
    msg.className = "msg";
    try {
      const r = await login(cu.valor.trim(), cp.valor);
      if (r.ok) { setToken((await r.json()).access_token); onLogged(); return; }
      msg.textContent = "Usuario o contraseña incorrectos.";
      msg.className = "msg error";
    } catch (_) {
      msg.textContent = "No se pudo conectar. Revisa tu conexión.";
      msg.className = "msg error";
    }
    boton.disabled = false;
  };

  // Modo visita. Es lo que permite ENSEÑAR el sistema: quien recibe el enlace
  // entra en un clic, con datos dentro, y entiende de qué va antes de decidir
  // si se registra. Sin esto, un desconocido choca contra un formulario y se va.
  const demo = window.__APP__.demo;
  if (demo && demo.usuario) {
    const caja = el.querySelector(".mirar");
    caja.innerHTML = `
      <hr>
      <p class="ayuda">¿Solo quieres mirar? Entra a la cuenta de ejemplo, que ya
      tiene ${window.__APP__.plural.toLowerCase()} dentro. Lo que crees ahí no se
      mezcla con tu cuenta.</p>
      <button class="ver ghost">Ver una demostración</button>`;
    caja.querySelector(".ver").onclick = async () => {
      msg.textContent = "Entrando a la demostración…";
      msg.className = "msg";
      const r = await login(demo.usuario, demo.clave);
      if (r.ok) { setToken((await r.json()).access_token); onLogged(); }
      else { msg.textContent = "La demostración no está disponible."; msg.className = "msg error"; }
    };
  }
  return el;
}
