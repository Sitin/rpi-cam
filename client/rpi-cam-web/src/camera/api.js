import { config } from '../config'
import { socket } from "../socket";


function getFullSrc(src) {
  if (!config.mediaPrefix) {
    return src;
  } else {
    return config.mediaPrefix + src;
  }
}

function subscribeToPreviews(cb) {
  socket.on('preview', data => {
    data.src = getFullSrc(data.src);
    return cb(null, data);
  });
}

function subscribeToImages(cb) {
  socket.on('image', data => {
    data.src = getFullSrc(data.src);
    data.thumbnail.src = getFullSrc(data.thumbnail.src);
    return cb(null, data);
  });
}

function subscribeToLatestImages(cb) {
  socket.on('latest images', data => {
    for (let img of data) {
      img.src = getFullSrc(img.src);
      img.thumbnail.src = getFullSrc(img.thumbnail.src);
    }
    return cb(null, data);
  });
}

function shootImage() {
  socket.emit('shoot');
}

export { subscribeToPreviews, subscribeToImages, subscribeToLatestImages, shootImage }
