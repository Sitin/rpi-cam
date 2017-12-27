def crop_to_ratio(img, ratio=4/3):
    (height, width, *_) = img.shape

    if width * ratio > height:
        target_width = int(height * ratio)
        target_height = height
    else:
        target_width = width
        target_height = int(width / ratio)

    left = (width - target_width) // 2
    right = target_width + (width - target_width) // 2
    top = (height - target_height) // 2
    bottom = target_height + (height - target_height) // 2

    return img[top:bottom, left:right]