import React, { Component } from 'react';
import nothing from './nothing.png';
import './App.css';

import { subscribeToPreviews, subscribeToImages, subscribeToLatestImages, shootImage } from './api';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">RPI Camera</h1>
        </header>
        <div className="App-content">
          <div>
            {this.imageJSX(this.state.last_preview, this.state.preview_width, true)}
          </div>
          <div>
            <button className="App-shoot-btn" onClick={shootImage}>Shoot</button>
          </div>
          {this.lastShotJSX()}
          <div className="App-gallery">
            {this.latestImagesJSX()}
          </div>
        </div>
        <footer className="App-footer">
          <p>Created by <a href="https://github.com/Sitin">Mikhail Zyatin</a>.</p>
          <p><a href="https://github.com/Sitin/rpi-cam">Source code</a></p>
        </footer>
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
    subscribeToLatestImages((err, latest_images) => this.setState({
      latest_images: latest_images
    }));
  }

  imageJSX = (img, width, fullSize) => (
    img ?
    <a href={img.src} title="Click to open full image">
      <img src={fullSize ? img.src : img.thumbnail.src} alt="Nothing to show."
           width={width}
           height={width / img.ratio}
      />
    </a> : undefined
  );

  lastShotJSX = () => (
    this.state.last_image ?
      <div>
        {this.imageJSX(this.state.last_image, this.state.image_width, true)}
      </div> : undefined
  );

  latestImagesJSX = () => this.state.latest_images.map(img => (
    <span key={img.src}>{this.imageJSX(img, this.state.gallery_image_width, false)}</span>
  ));

  state = {
    last_preview: {src: nothing, ratio: 4/3},
    last_image: null,
    latest_images: [],
    preview_width: 320,
    image_width: 320,
    gallery_image_width: 160,
  };
}

export default App;
