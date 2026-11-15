def choose_indices(frame_count, quota, pins):
    if (type(frame_count) is not int or type(quota) is not int or
            not 1 <= quota <= frame_count or
            any(type(i) is not int or not 0 <= i < frame_count for i in pins)):
        raise ValueError('SAMPLING_INPUT_INVALID')
    indices = set(pins)
    if len(indices) > quota:
        raise ValueError('PINNED_FRAMES_EXCEED_QUOTA')
    if quota == 1:
        return sorted(indices or {frame_count // 2})
    indices.update((0, frame_count - 1))
    if len(indices) > quota:
        raise ValueError('PINNED_QUOTA_CANNOT_SPAN_SOURCE')
    for grid_count in (max(2, quota-len(indices)+2), quota*2+1, frame_count):
        for i in range(grid_count):
            if len(indices) >= quota:
                break
            indices.add(round((frame_count-1)*i/(grid_count-1)))
        if len(indices) >= quota:
            break
    return sorted(indices)
