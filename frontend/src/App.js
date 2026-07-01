import React, { useEffect, useState } from "react";
import API from "./api/api";

function App() {
const [loads, setLoads] = useState([]);
const [dashboard, setDashboard] = useState({});
const [gridStatus, setGridStatus] = useState({});
const [alerts, setAlerts] = useState([]);
const [predictions, setPredictions] = useState([]);
const [recommendations, setRecommendations] = useState([]);
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
     API.get("/grid-status")
  .then((response) => {
    console.log("Grid:", response.data);
    setGridStatus(response.data);
  })
  .catch((error) => {
    console.error(error);
  });
  API.get("/alerts")
  .then((response) => {
    console.log("Alerts:", response.data);
    setAlerts(response.data);
  })
  .catch((error) => {
    console.error(error);
  });
  API.get("/prediction")
  .then((response) => {
    console.log("Prediction:", response.data);
    setPredictions(response.data);
  })
  .catch((error) => {
    console.error(error);
  });
  API.get("/recommendations")
  .then((response) => {
    console.log("Recommendations:", response.data);
    setRecommendations(response.data);
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
<div className="card mb-4">
  <div className="card-body text-center">

    <h4>Grid Health Status</h4>

    <h2>{gridStatus.grid_status}</h2>

  </div>
</div>
</div>
<div className="card mb-4">
  <div className="card-header bg-warning">
    <h4>⚠ Grid Alerts</h4>
  </div>

  <div className="card-body">

    {alerts.length === 0 ? (

      <p>No overloaded sectors.</p>

    ) : (

      <ul className="list-group">

        {alerts.map((alert, index) => (

          <li key={index} className="list-group-item">

            <strong>{alert.area}</strong> -

            Current Load: {alert.current_load}

            {" / "}

            Capacity: {alert.max_capacity}

            {" ("}

            {alert.usage_percent}%

            {")"}

          </li>

        ))}

      </ul>

    )}

  </div>
</div>
<div className="card mb-4">

  <div className="card-header bg-info text-white">
    <h4>📈 Load Prediction</h4>
  </div>

  <div className="card-body">

    <table className="table table-bordered">

      <thead>

        <tr>
          <th>Area</th>
          <th>Current Load</th>
          <th>Predicted Load</th>
        </tr>

      </thead>

      <tbody>

        {predictions.map((item, index) => (

          <tr key={index}>

            <td>{item.area}</td>

            <td>{item.current_load}</td>

            <td>{item.predicted_load}</td>

          </tr>

        ))}

      </tbody>

    </table>

  </div>

</div>
<div className="card mb-4">

  <div className="card-header bg-success text-white">
    <h4>💡 Smart Recommendations</h4>
  </div>

  <div className="card-body">

    <table className="table table-bordered table-hover">

      <thead className="table-light">

        <tr>
          <th>Area</th>
          <th>Usage %</th>
          <th>Recommendation</th>
        </tr>

      </thead>

      <tbody>

        {recommendations.map((item, index) => (

          <tr key={index}>

            <td>{item.area}</td>

            <td>{item.usage_percent}%</td>

            <td>{item.recommendation}</td>

          </tr>

        ))}

      </tbody>

    </table>

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