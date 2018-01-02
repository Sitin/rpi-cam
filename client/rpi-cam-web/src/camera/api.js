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

    this.settings = null;
    this.preview = null;
    this.lastImage = null;
    this.latestImages = null;

    this.setupListeners();
  }

  setupListeners() {
    const self = this;

    socket.on('settings', data => {
      console.log('Camera settings:', data);
      self.settings = data;
      self.emit('settings changed');
    });

    socket.on('preview', data => {
      self.preview = processImageData(data);
      self.emit('preview changed');
    });

    socket.on('disconnect', () => {
      self.preview = null;
      self.emit('preview changed');
    });

    socket.on('image', data => {
      self.lastImage = processImageData(data);
      self.emit('last image changed');
    });

    socket.on('latest images', data => {
      for (let img of data) {
        processImageData(img);
      }
      self.latestImages = data;
      self.emit('latest images changed');
    });
  }

  getSettings() {
    return this.settings;
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

  updateSettings(settings) {
    socket.emit('update settings', settings);
  }

  subscribeToSettingsChange(cb) {
    this.on('settings changed', cb);
  }

  unsubscribeFromSettingsChange(cb) {
    this.off('settings changed', cb);
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
