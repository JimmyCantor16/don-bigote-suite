// PANTALLA DE CREAR CUENTA. Separada de la de entrar (login.js).
import { register } from "../api.js";
import { reglas, campo, gobernar } from "../validacion.js";

export function RegistroView(onRegistrado, irALogin) {
  const el = document.createElement("section");
  el.className = "card";
  // Igual que en la pantalla de entrar: <form> real, para que el Enter envíe y
  // el gestor de contraseñas ofrezca guardar la cuenta recién creada.
  el.innerHTML = `
    <h1>Crear cuenta</h1>
    <p class="sub"></p>
    <form class="alta-cuenta" novalidate>
      <label for="ru">Usuario</label>
      <input id="ru" class="u" name="username" autocomplete="username" aria-describedby="ru-err">
      <p class="u-error error-campo" id="ru-err" role="alert"></p>
      <label for="rp">Contraseña</label>
      <input id="rp" class="p" name="new-password" type="password" autocomplete="new-password" aria-describedby="rp-err">
      <p class="p-error error-campo" id="rp-err" role="alert"></p>
      <label for="rr">Repite la contraseña</label>
      <input id="rr" class="r" name="confirm-password" type="password" autocomplete="new-password" aria-describedby="rr-err">
      <p class="r-error error-campo" id="rr-err" role="alert"></p>
      <p class="ayuda">Usuario: 3 caracteres o más. Contraseña: 8 o más, con letras y números.</p>
      <div class="row">
        <button class="up" type="submit" disabled>Crear mi cuenta</button>
      </div>
    </form>
    <p class="msg" role="status" aria-live="polite"></p>
    <p class="ayuda">¿Ya tienes cuenta? <a href="#/login" class="ir-login">Entra aquí</a>.</p>`;

  el.querySelector(".sub").textContent =
    "Regístrate para gestionar tus " + window.__APP__.plural.toLowerCase() + ".";

  const msg = el.querySelector(".msg");
  const boton = el.querySelector(".up");
  const cu = campo(el, "u", reglas.usuario, () => repintar());
  // Al cambiar la contraseña hay que refrescar la de confirmación: si no, se
  // queda diciendo "no coinciden" cuando ya coinciden.
  const cp = campo(el, "p", reglas.clave, () => { cr.refrescar(); repintar(); });
  const cr = campo(el, "r", (v) => reglas.repetir(v, cp.valor), () => repintar());
  const repintar = gobernar(boton, [cu, cp, cr]);

  el.querySelector(".ir-login").onclick = (e) => { e.preventDefault(); irALogin(); };

  el.querySelector("form.alta-cuenta").onsubmit = async (e) => {
    e.preventDefault();
    // Se revisan los tres a la vez para que el usuario vea TODO lo que falta,
    // no un error, lo arregle, y descubra el siguiente.
    const errores = [cu.revisar(), cp.revisar(), cr.revisar()].filter(Boolean);
    if (errores.length) return;
    boton.disabled = true;
    msg.textContent = "Creando tu cuenta…";
    msg.className = "msg";
    try {
      const r = await register(cu.valor.trim(), cp.valor);
      if (r.ok) {
        msg.textContent = "Cuenta creada. Te llevamos a entrar…";
        msg.className = "msg ok";
        setTimeout(() => onRegistrado(cu.valor.trim()), 900);
        return;
      }
      const d = await r.json().catch(() => ({}));
      msg.textContent = d.detail || "No se pudo crear la cuenta.";
      msg.className = "msg error";
    } catch (_) {
      msg.textContent = "No se pudo conectar. Revisa tu conexión.";
      msg.className = "msg error";
    }
    boton.disabled = false;
  };
  return el;
}
