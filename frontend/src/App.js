import React, { useEffect, useState } from "react";
import API from "./api/api";

function App() {
const [loads, setLoads] = useState([]);

 useEffect(() => {
  API.get("/loads")
    .then((response) => {
      console.log("DATA:", response.data);
      setLoads(response.data);
    })
    .catch((error) => {
      console.error(error);
    });
}, []);

  return (
    <div className="container mt-5">

      <h1 className="text-center mb-4">
        Smart Grid Dashboard
      </h1>

      <table className="table table-bordered table-striped">

        <thead className="table-dark">
          <tr>
            <th>Area</th>
            <th>Current Load</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
  {loads.map((item, index) => (
    <tr key={index}>
      <td>{item.area}</td>
      <td>{item.current_load}</td>
      <td>
        {item.current_load > 90
          ? "Overloaded"
          : "Normal"}
      </td>
    </tr>
  ))}
</tbody>

      </table>

    </div>
  );
}

export default App;