import React from 'react';

function Image(props) {
  if (props.img) {
    const src = props.preview && !!props.img['thumbnail'] ?
      props.img.thumbnail.src : props.img.src;

    const imageTag = <img src={src} alt="Nothing to show."
                width={props.width}
                height={props.width / props.img.ratio}
    />;

    if (props.openable) {
      return <a href={props.img.src} title="Click to open full image">{imageTag}</a>
    } else {
      return imageTag;
    }
  } else {
    return null;
  }
}

export { Image }