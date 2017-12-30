import React, { Component } from 'react';

import { Panel } from 'react-bootstrap';

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
    return <Panel>
      {this.state.images.map(img =>
        <span key={img.src}>
          <Image img={img} width={this.props.imageWidth} preview={true} openable={true} />
        </span>
      )}
    </Panel>;
  }

  state = {
    images: [],
  };
}

export { LatestShots }
