import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import "./App.css";

function App() {
  // pamti koju formu prikazujemo: "login" ili "register"
  const [prikaz, setPrikaz] = useState("login");

  return (
    <div>
      {prikaz === "login" ? (
        <Login onSwitch={() => setPrikaz("register")} />
      ) : (
        <Register onSwitch={() => setPrikaz("login")} />
      )}
    </div>
  );
}

export default App;