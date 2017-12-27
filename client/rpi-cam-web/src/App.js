import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import { subscribeToThumbs, subscribeToImages, shootImage } from './api';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">RPI Camera</h1>
        </header>
        <div>
          <img src={this.state.last_thumb.src} alt="Opening camera..."
               width={this.state.thumb_width}
               height={this.state.thumb_width / this.state.last_thumb.ratio}
          />
        </div>
        <div>
          <button onClick={shootImage}>Shoot</button>
        </div>
        <p className="App-intro">Last shot:</p>
        <div>
          <img src={this.state.last_image.src} alt="Nothing to show."
               width={this.state.image_width}
               height={this.state.image_width / this.state.last_image.ratio}
          />
        </div>
      </div>
    );
  }

  constructor(props) {
    super(props);
    subscribeToThumbs((err, last_frame) => this.setState({
      last_thumb: last_frame
    }));
    subscribeToImages((err, last_image) => this.setState({
      last_image: last_image
    }));
  }

  state = {
    last_thumb: {src: '/static/media/nothing.jpg', ratio: 4/3},
    last_image: {src: '/static/media/nothing.jpg', ratio: 4/3},
    thumb_width: 320,
    image_width: 600,
  };
}

export default App;
