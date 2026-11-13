# Especificación y plan

## Qué se construye
Don Bigote Suite es una aplicación web para una cadena de barberías con inicio de sesión y registro, que permite gestionar clientes (con historial y puntos de fidelidad), servicios, barberos con comisión y citas por sede, y ofrece un panel con las citas de hoy, lo facturado y la comisión de cada barbero.

## Pantallas que verás
- Inicio de sesión
- Registro de usuario
- Panel (citas de hoy, facturación del día y comisión por barbero)
- Clientes (lista con búsqueda, puntos de fidelidad y estado vacío cuidado)
- Detalle de cliente (historial de citas y puntos acumulados)
- Servicios (lista con precio y duración)
- Barberos (lista con porcentaje de comisión y sede)
- Citas (lista filtrable por fecha, sede, barbero y estado)
- Nueva cita / Editar cita (formulario con fecha, hora, sede, barbero, cliente, servicio y estado)
- Sedes (lista de sucursales)
- Mensajes de error y página no encontrada

## Datos del sistema
- Usuario (nombre, correo, contraseña, rol)
- Sede (nombre, dirección, teléfono)
- Cliente (nombre, teléfono, correo, puntos de fidelidad)
- Servicio (nombre, precio, duración en minutos)
- Barbero (nombre, sede, porcentaje de comisión)
- Cita (fecha, hora, sede, barbero, cliente, servicio, estado: pendiente/confirmada/atendida/cancelada, monto)

## API del backend
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- GET /api/dashboard
- GET /api/branches
- POST /api/branches
- GET /api/clients
- POST /api/clients
- GET /api/clients/:id
- PUT /api/clients/:id
- DELETE /api/clients/:id
- GET /api/clients/:id/appointments
- GET /api/services
- POST /api/services
- PUT /api/services/:id
- DELETE /api/services/:id
- GET /api/barbers
- POST /api/barbers
- PUT /api/barbers/:id
- DELETE /api/barbers/:id

## Para considerarlo funcional, debes VER
- Al abrir la app sin sesión se ve un formulario de inicio de sesión con enlace a registro; tras ingresar con credenciales válidas se llega al panel, y con credenciales erróneas se ve un mensaje de error claro
- El panel muestra tarjetas con números: citas de hoy, total facturado del día y citas atendidas, más una tabla con las citas de hoy (hora, cliente, barbero, servicio, sede, estado con color)
- El panel muestra una tabla o gráfica con la comisión calculada de cada barbero (nombre, servicios atendidos, facturado y comisión en dinero)
- La pantalla de Clientes muestra una tabla con filas de clientes, sus puntos de fidelidad y un buscador que filtra al escribir; al abrir uno se ve su historial de citas
- La pantalla de Servicios muestra tarjetas o filas con nombre, precio y duración, y permite crear y editar
- La pantalla de Barberos muestra cada barbero con su sede y su porcentaje de comisión
- La pantalla de Citas muestra una tabla con fecha, hora, sede, barbero, cliente y un estado con insignia de color (pendiente, confirmada, atendida, cancelada), con filtros y un botón para cambiar el estado
- Al marcar una cita como atendida, el panel actualiza lo facturado y la comisión del barbero, y el cliente suma puntos de fidelidad visibles
- Cada lista sin datos muestra un estado vacío amable con un botón de acción, y los fallos de carga muestran un mensaje de error con opción de reintentar
- La app se ve bien y es usable en celular y en escritorio, con navegación por teclado, etiquetas en formularios y contraste legible

## Stack
Frontend React con Vite y diseño responsive (CSS moderno), backend Node.js con Express y autenticación JWT, y base de datos SQLite con datos de ejemplo precargados al iniciar
