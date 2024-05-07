import React, { useState } from 'react';
import './App.css';

function App() {
  // Estados para almacenar datos del formulario
  const [registroData, setRegistroData] = useState({ nombreUsuario: '', contraseña: '' });
  const [loginData, setLoginData] = useState({ nombreUsuario: '', contraseña: '' });
  const [autenticado, setAutenticado] = useState(false);

  // Función para manejar el envío del formulario de registro
  const handleRegistroSubmit = async (event) => {
    event.preventDefault();
    try {
      // Enviar los datos de registro al backend
      const response = await fetch('http://127.0.0.1:5000/registro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registroData),
      });
      const data = await response.json();
      if (response.ok) {
        console.log('Registro exitoso:', data);
        // Limpiar el formulario después del registro exitoso
        setRegistroData({ nombreUsuario: '', contraseña: '' });
      } else {
        console.error('Error en el registro:', data.error);
      }
    } catch (error) {
      console.error('Error al enviar solicitud de registro:', error);
    }
  };

  // Función para manejar el envío del formulario de inicio de sesión
  const handleLoginSubmit = async (event) => {
    event.preventDefault();
    try {
      // Enviar los datos de inicio de sesión al backend
      const response = await fetch('http://127.0.0.1:5000/autenticacion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });
      const data = await response.json();
      if (response.ok) {
        console.log('Inicio de sesión exitoso:', data);
        // Marcar al usuario como autenticado
        setAutenticado(true);
        // Limpiar el formulario después del inicio de sesión exitoso
        setLoginData({ nombreUsuario: '', contraseña: '' });
      } else {
        console.error('Error en el inicio de sesión:', data.error);
      }
    } catch (error) {
      console.error('Error al enviar solicitud de inicio de sesión:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Aplicación de Autenticación</h1>
        {/* Formulario de registro */}
        <form onSubmit={handleRegistroSubmit}>
          <h2>Registro</h2>
          <input
            type="text"
            placeholder="Nombre de usuario"
            value={registroData.nombreUsuario}
            onChange={(e) => setRegistroData({ ...registroData, nombreUsuario: e.target.value })}
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={registroData.contraseña}
            onChange={(e) => setRegistroData({ ...registroData, contraseña: e.target.value })}
          />
          <button type="submit">Registrarse</button>
        </form>
        {/* Formulario de inicio de sesión */}
        <form onSubmit={handleLoginSubmit}>
          <h2>Iniciar Sesión</h2>
          <input
            type="text"
            placeholder="Nombre de usuario"
            value={loginData.nombreUsuario}
            onChange={(e) => setLoginData({ ...loginData, nombreUsuario: e.target.value })}
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={loginData.contraseña}
            onChange={(e) => setLoginData({ ...loginData, contraseña: e.target.value })}
          />
          <button type="submit">Iniciar Sesión</button>
        </form>
        {/* Contenido secreto */}
        {autenticado && (
          <div>
            <h2>Contenido Secreto</h2>
            <p>¡Bienvenido! Has iniciado sesión correctamente.</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
