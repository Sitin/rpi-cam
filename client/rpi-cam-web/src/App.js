import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import { subscribeToPreviews, subscribeToImages, subscribeToLatestImages, shootImage } from './api';

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
          <button className="App-shoot-btn" onClick={shootImage}>Shoot</button>
        </div>
        {this.lastShotJSX()}
        <div>
          {this.latestImagesJSX()}
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

  latestImagesJSX = () => this.state.latest_images.map(img =>
    this.imageJSX(img, this.state.gallery_image_width, false));

  state = {
    last_preview: {src: '/static/media/nothing.jpg', ratio: 4/3},
    last_image: null,
    latest_images: [],
    preview_width: 320,
    image_width: 320,
    gallery_image_width: 160,
  };
}

export default App;
