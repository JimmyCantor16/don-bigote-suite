// Validación que corre ANTES de enviar nada al servidor.
// El servidor vuelve a validar siempre: esto es comodidad, no seguridad.

export const reglas = {
  usuario(v) {
    const s = (v || "").trim();
    if (!s) return "Escribe tu usuario.";
    if (s.length < 3) return "Al menos 3 caracteres.";
    if (s.length > 30) return "Como mucho 30 caracteres.";
    if (!/^[a-zA-Z0-9._-]+$/.test(s)) return "Solo letras, números, punto, guion y guion bajo.";
    return "";
  },
  clave(v) {
    const s = v || "";
    if (!s) return "Escribe una contraseña.";
    if (s.length < 8) return "Al menos 8 caracteres.";
    if (!/[a-zA-Z]/.test(s)) return "Debe llevar alguna letra.";
    if (!/[0-9]/.test(s)) return "Debe llevar algún número.";
    return "";
  },
  claveDeEntrada(v) {
    // Al entrar no se re-exige la política: la cuenta puede ser antigua. Solo
    // que no vaya vacía, para no gastar un viaje al servidor por nada.
    return (v || "") ? "" : "Escribe tu contraseña.";
  },
  repetir(v, original) {
    if (!(v || "")) return "Repite la contraseña.";
    if (v !== original) return "Las dos contraseñas no coinciden.";
    return "";
  },
};

/**
 * Enlaza un input con su hueco de error.
 *
 * El error se muestra PEGADO AL CAMPO que lo causa, no en un aviso global: así
 * el usuario ve cuál de los tres campos tiene que arreglar. Y no se le regaña
 * mientras escribe la primera vez — solo al salir del campo o al intentar
 * enviar — porque marcar en rojo desde la primera letra es hostil.
 */
export function campo(raiz, clase, validar, alCambiar) {
  const input = raiz.querySelector("." + clase);
  const hueco = raiz.querySelector("." + clase + "-error");
  let tocado = false;

  function pintar(forzar) {
    const error = validar(input.value);
    const visible = (tocado || forzar) ? error : "";
    hueco.textContent = visible;
    input.setAttribute("aria-invalid", visible ? "true" : "false");
    input.classList.toggle("malo", Boolean(visible));
    return error;
  }

  input.addEventListener("blur", () => { tocado = true; pintar(false); });
  input.addEventListener("input", () => { if (tocado) pintar(false); alCambiar(); });
  return {
    get valor() { return input.value; },
    get valido() { return !validar(input.value); },
    revisar: () => { tocado = true; return pintar(true); },
    // Repinta sin marcar como tocado. Lo necesita el campo "repite la
    // contraseña": si cambias la de arriba, su error debe actualizarse solo.
    refrescar: () => pintar(false),
    foco: () => input.focus(),
  };
}

/** Deshabilita el botón mientras el formulario no sea válido. */
export function gobernar(boton, campos) {
  const repintar = () => { boton.disabled = !campos.every((c) => c.valido); };
  repintar();
  return repintar;
}
