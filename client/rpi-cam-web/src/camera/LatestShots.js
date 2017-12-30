import React, { Component } from 'react';
import './LatestShots.css';

import { subscribeToLatestImages } from './api';
import { Image } from '../shared/Image';

class LatestShots extends Component {
  constructor(props) {
    super(props);

    subscribeToLatestImages((err, images) => this.setState({
      images: images
    }));
  }

  render() {
    return <div className="LatestShots">
      {this.state.images.map(img =>
        <span key={img.src}>
          <Image img={img} width={this.props.imageWidth} preview={true} openable={true} />
        </span>
      )}
    </div>;
  }

  state = {
    images: [],
  };
}

export { LatestShots }
