import { useState } from "react";

function Register({ onSwitch }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [poruka, setPoruka] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPoruka("");

    try {
      const response = await fetch("http://localhost:8001/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          password,
          password_confirmation: passwordConfirm,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setPoruka("Uspešna registracija! 🎉 Sad se možeš prijaviti.");
      } else {
        setPoruka(
          typeof data.detail === "string"
            ? data.detail
            : "Greška pri registraciji. Proveri podatke."
        );
      }
    } catch (error) {
      setPoruka("Ne mogu da se povežem sa serverom. Da li backend radi?");
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Registracija</h2>

        <label>Ime</label>
        <input type="text" value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Tvoje ime" required />

        <label>Email</label>
        <input type="email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="primer@email.com" required />

        <label>Lozinka</label>
        <input type="password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••" required />

        <label>Potvrdi lozinku</label>
        <input type="password" value={passwordConfirm}
          onChange={(e) => setPasswordConfirm(e.target.value)}
          placeholder="••••••••" required />

        <button type="submit">Registruj se</button>

        {poruka && <p className="poruka">{poruka}</p>}

        <p className="prebaci-link">
          Već imaš nalog? <span onClick={onSwitch}>Prijavi se</span>
        </p>
      </form>
    </div>
  );
}

export default Register;