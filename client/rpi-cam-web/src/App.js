import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import { subscribeToPreviews, subscribeToImages, shootImage } from './api';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">RPI Camera</h1>
        </header>
        <div>
          <img src={this.state.last_preview.src} alt="Opening camera..."
               width={this.state.preview_width}
               height={this.state.preview_width / this.state.last_preview.ratio}
               onClick={shootImage}
               title="Click to shoot"
          />
        </div>
        <div>
          <button onClick={shootImage}>Shoot</button>
        </div>
        <p className="App-intro">Last shot:</p>
        <div>
          <a href={this.state.last_image.src} title="Click to open full image">
            <img src={this.state.last_image.thumbnail.src} alt="Nothing to show."
                 width={this.state.image_width}
                 height={this.state.image_width / this.state.last_image.ratio}
            />
          </a>
        </div>
      </div>
    );
  }

  constructor(props) {
    super(props);
    subscribeToPreviews((err, last_frame) => this.setState({
      last_preview: last_frame
    }));
    subscribeToImages((err, last_image) => this.setState({
      last_image: last_image
    }));
  }

  state = {
    last_preview: {src: '/static/media/nothing.jpg', ratio: 4/3},
    last_image: {src: '/static/media/nothing.jpg', ratio: 4/3, thumbnail: {
      src: '/static/media/nothing.jpg', ratio: 4/3
    }},
    preview_width: 320,
    image_width: 320,
  };
}

export default App;
