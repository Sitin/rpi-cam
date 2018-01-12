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
    this.fps = 0;
    this.messages = [];

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

    socket.on('fps', data => {
      self.fps = data.fps;
      self.emit('fps changed');
    });

    socket.on('log', data => {
      console.log('Got log message from server:', data);
      self.messages.unshift(data);
      self.emit('got message');
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

  getFPS() {
    return this.fps;
  }

  getMessages() {
    return this.messages;
  }

  shootImage() {
    socket.emit('shoot');
  }

  updateSettings(settings) {
    socket.emit('update settings', settings);
  }

  subscribeToSettings(cb) {
    this.on('settings changed', cb);
  }

  unsubscribeFromSettings(cb) {
    this.off('settings changed', cb);
  }

  subscribeToPreview(cb) {
    this.on('preview changed', cb);
  }

  unsubscribeFromPreview(cb) {
    this.off('preview changed', cb);
  }

  subscribeToLastImage(cb) {
    this.on('last image changed', cb)
  }

  unsubscribeFromLastImage(cb) {
    this.off('last image changed', cb)
  }

  subscribeToLatestImages(cb) {
    this.on('latest images changed', cb);
  }

  unsubscribeFromLatestImages(cb) {
    this.off('latest images changed', cb);
  }

  subscribeToFPS(cb) {
    this.on('fps changed', cb);
  }

  unsubscribeFromFPS(cb) {
    this.off('fps changed', cb);
  }

  subscribeToMessages(cb) {
    this.on('got message', cb);
  }

  unsubscribeFromErrors(cb) {
    this.off('got message', cb);
  }
}

const cameraApi = new CameraApi();

export { cameraApi }
