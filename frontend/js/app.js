// Entrada y enrutador. Entrar y registrarse son DOS pantallas distintas,
// cada una con su dirección (#/login y #/registro), para que se pueda enlazar
// y compartir cada una por separado y el botón "atrás" del navegador funcione.
import { LoginView } from "./components/login.js";
import { RegistroView } from "./components/registro.js";
import { BoardView } from "./components/board.js";
import { isLogged } from "./state.js";

const root = document.getElementById("app");

function ir(ruta) {
  if (location.hash === ruta) render();
  else location.hash = ruta;
}

function render() {
  root.innerHTML = "";
  if (isLogged()) {
    root.appendChild(BoardView(render));
    return;
  }
  if (location.hash === "#/registro") {
    root.appendChild(RegistroView(() => ir("#/login"), () => ir("#/login")));
  } else {
    root.appendChild(LoginView(() => ir("#/"), () => ir("#/registro")));
  }
  window.scrollTo(0, 0);
}

window.addEventListener("hashchange", render);
render();
