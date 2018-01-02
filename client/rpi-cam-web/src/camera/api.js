import EventEmitter from 'eventemitter3';

import { config } from '../config'
import { socket } from '../socket';


function getFullSrc(src) {
  if (!config.mediaPrefix) {
    return src;
  } else {
    return config.mediaPrefix + src;
  }
}

function processImageData(data) {
  data.src = getFullSrc(data.src);
  if (typeof data['thumbnail'] === 'object') {
    data.thumbnail.src = getFullSrc(data.thumbnail.src);
  }
  return data;
}

class CameraApi extends EventEmitter {
  constructor() {
    super();

    this.preview = null;
    this.lastImage = null;
    this.latestImages = null;

    this.setupListeners();
  }

  setupListeners() {
    const self = this;

    socket.on('preview', data => {
      self.preview = processImageData(data);
      self.emit('preview changed');
      return true;
    });

    socket.on('disconnect', () => {
      self.preview = null;
      self.emit('preview changed');
      return true;
    });

    socket.on('image', data => {
      self.lastImage = processImageData(data);
      self.emit('last image changed');
      return true;
    });

    socket.on('latest images', data => {
      for (let img of data) {
        processImageData(img);
      }
      self.latestImages = data;
      self.emit('latest images changed');
      return true;
    });
  }

  getPreview() {
    return this.preview;
  }

  getLastImage() {
    return this.lastImage;
  }

  getLatestImages() {
    return this.latestImages;
  }

  shootImage() {
    socket.emit('shoot');
  }

  subscribeToPreviewChange(cb) {
    this.on('preview changed', cb);
  }

  unsubscribeFromPreviewChange(cb) {
    this.off('preview changed', cb);
  }

  subscribeToLastImageChange(cb) {
    this.on('last image changed', cb)
  }

  unsubscribeFromLastImageChange(cb) {
    this.off('last image changed', cb)
  }

  subscribeToLatestImagesChange(cb) {
    this.on('latest images changed', cb);
  }

  unsubscribeFromLatestImagesChange(cb) {
    this.off('latest images changed', cb);
  }
}

const cameraApi = new CameraApi();

export { cameraApi }
