import io from 'socket.io-client';
import { config } from './config'

const  socket = io(config.apiRoot + '/cam');


function getFullSrc(src) {
  if (!config.mediaPrefix) {
    return src;
  } else {
    return config.mediaPrefix + src;
  }
}

function subscribeToThumbs(cb) {
  socket.on('thumb', data => {
    const src = data['src'] || '/static/media/nothing.jpg';
    return cb(null, {
      src: getFullSrc(src),
      ratio: data['ratio'] || 4/3,
    });
  });
}

function subscribeToImages(cb) {
  socket.on('image', data => {
    const src = data['src'] || '/static/media/nothing.jpg';
    return cb(null, {
      src: getFullSrc(src),
      ratio: data['ratio'] || 4/3,
    });
  });
}

function shootImage() {
  socket.emit('shoot');
}

export { subscribeToThumbs, subscribeToImages, shootImage }
