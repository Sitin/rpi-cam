import React, { Component } from 'react';
import nothing from './nothing.png';

import { Image } from '../shared/Image';

import { subscribeToPreviews, shootImage } from './api';

import './Camera.css';

class Camera extends Component {
  constructor(props) {
    super(props);

    subscribeToPreviews((err, lastFrame) => this.setState({
      lastFrame: lastFrame
    }));
  }

  render() {
    return <div className="Camera">
      <div className="Camera-preview">
        <a title="Click to shoot image" onClick={shootImage}>
          <Image img={this.state.lastFrame} width={this.props.imageWidth} />
        </a>
      </div>
      <div>
        <button className="Camera-shoot-btn" onClick={shootImage}>Shoot</button>
      </div>
    </div>;
  }

  state = {
    lastFrame: {src: nothing, ratio: 4/3},
  };
}

export { Camera }
