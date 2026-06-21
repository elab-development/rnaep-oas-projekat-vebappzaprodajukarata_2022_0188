import { useState } from "react";

function Login({ onSwitch }) {
  // "state" = mesto gde čuvamo šta korisnik ukuca
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [poruka, setPoruka] = useState("");

  // ova funkcija se pokreće kad se klikne "Prijavi se"
  const handleSubmit = async (e) => {
    e.preventDefault(); // spreči osvežavanje stranice
    setPoruka("");

    try {
      // šaljemo podatke na TVOJ backend (login endpoint)
      const response = await fetch("http://localhost:8001/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setPoruka("Uspešna prijava! 🎉");
        console.log("JWT token:", data.access_token);
        // kasnije ćemo token sačuvati (localStorage) za zaštićene rute
      } else {
        setPoruka(data.detail || "Pogrešan email ili lozinka.");
      }
    } catch (error) {
      setPoruka("Ne mogu da se povežem sa serverom. Da li backend radi?");
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Prijava</h2>

        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="primer@email.com"
          required
        />

        <label>Lozinka</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          required
        />

        <button type="submit">Prijavi se</button>

        {poruka && <p className="poruka">{poruka}</p>}

        <p className="prebaci-link">
          Nemaš nalog? <span onClick={onSwitch}>Registruj se</span>
        </p>
      </form>
    </div>
  );
}

export default Login;