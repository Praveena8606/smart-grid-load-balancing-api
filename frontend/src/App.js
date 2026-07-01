import React, { useEffect, useState } from "react";
import API from "./api/api";

function App() {
const [loads, setLoads] = useState([]);
const [dashboard, setDashboard] = useState({});
useEffect(() => {

  API.get("/loads")
    .then((response) => {
      console.log("DATA:", response.data);
      setLoads(response.data);
    })
    .catch((error) => {
      console.error(error);
    });

  API.get("/dashboard")
    .then((response) => {
      console.log("Dashboard:", response.data);
      setDashboard(response.data);
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
         <div className="row mb-4">

  <div className="col-md-4">
    <div className="card text-white bg-primary">
      <div className="card-body">
        <h5>Total Sectors</h5>
        <h2>{dashboard.total_sectors}</h2>
      </div>
    </div>
  </div>

  <div className="col-md-4">
    <div className="card text-white bg-danger">
      <div className="card-body">
        <h5>Overloaded</h5>
        <h2>{dashboard.overloaded_sectors}</h2>
      </div>
    </div>
  </div>

  <div className="col-md-4">
    <div className="card text-white bg-success">
      <div className="card-body">
        <h5>Average Usage</h5>
        <h2>{dashboard.average_usage}%</h2>
      </div>
    </div>
  </div>

</div>
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