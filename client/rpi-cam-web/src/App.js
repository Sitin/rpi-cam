import React, { Component } from 'react';
import './App.css';

import { Camera } from './camera/Camera';
import { LastShot } from './camera/LastShot';
import { LatestShots } from './camera/LatestShots';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">RPI Camera</h1>
        </header>

        <div className="App-content">
          <Camera imageWidth={320} />
          <LastShot imageWidth={320} />
          <LatestShots imageWidth={160} />
        </div>

        <footer className="App-footer">
          <p>Created by <a href="https://github.com/Sitin">Mikhail Zyatin</a>.</p>
          <p><a href="https://github.com/Sitin/rpi-cam">Source code</a></p>
        </footer>
      </div>
    );
  }
}

export default App;
