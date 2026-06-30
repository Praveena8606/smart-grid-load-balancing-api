import './App.css';

function App() {
  return (
    <div className="container mt-5">

      <h1 className="text-center text-primary">
        Smart Grid Load Balancing Dashboard
      </h1>

      <p className="text-center">
        Grid Operator Monitoring System
      </p>

      <hr />

      <div className="row">

        <div className="col-md-4">
          <div className="card text-center">
            <div className="card-body">
              <h5>Total Sectors</h5>
              <h2>0</h2>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card text-center">
            <div className="card-body">
              <h5>Overloaded Sectors</h5>
              <h2>0</h2>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card text-center">
            <div className="card-body">
              <h5>Average Usage</h5>
              <h2>0%</h2>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}

export default App;