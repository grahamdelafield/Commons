import numpy as np

value_map = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
}

hex_map = {v: k for (k, v) in value_map.items()}


def _chunk_code(hex):
    """Chunk the R, G, B components of hex code"""
    if hex.startswith("#"):
        hex = hex.replace("#", "")
    chunks = [hex[i : i + 2] for i in range(0, len(hex), 2)]
    return chunks


def _hex_to_val(hex):
    """Map a two digit hex to number."""
    bucket, step = value_map[hex[0]], value_map[hex[1]]
    return bucket * 16 + step + 1


def _val_to_hex(val):
    """Map a number ot a two digit hex."""
    bucket, step = divmod(val, 16)
    if step == 0:
        bucket -= 1
        step = 15
    return hex_map[bucket] + hex_map[step]


def _generate_gradient_two(val1, val2, steps=20):
    """Generate two point gradient of values."""
    vals = np.linspace(val1, val2, steps) // 1
    return [int(i) for i in vals]


def _generate_gradient_three(val1, val2, val3, steps=20):
    """Generate three point gradient of values."""
    first = np.linspace(val1, val2, steps) // 1
    first = [int(i) for i in first]
    second = np.linspace(val2, val3, steps) // 1
    second = [int(i) for i in second][1:]
    return first + second

def _grab_gradient_parts(gradient, number_desired):
    """Get the portions of the gradient you want."""
    assert number_desired >= 2, "Cannot create a single point gradient"
    first, last = gradient[0], gradient[-1]
    num_left = number_desired - 2
    if num_left == 0:
        return [first, last]
    stride_len = len(gradient) // (num_left + 1)
    selected = [gradient[n] for n in range(0 + stride_len, len(gradient), stride_len)]
    selected = selected[:num_left]
    return [first] + selected + [last]


def generate_colors(colors, number_wanted):
    """Generates concise series of colors mapped between provided endpoints.
    
    :arg colors:    (list)  list of hexcode colors to be used as gradient endpoints
    :arg number_wanted: (int)   number of colors to be returned"""
    chunks = [_chunk_code(c) for c in colors]
    vals = [[_hex_to_val(h) for h in chunk] for chunk in chunks]
    pairs = [z for z in zip(*vals)]
    if len(colors) == 2:
        gradients = [_generate_gradient_two(p[0], p[1]) for p in pairs]
    if len(colors) == 3:
        gradients = [_generate_gradient_three(p[0], p[1], p[2]) for p in pairs]
    grad_parts = [_grab_gradient_parts(grad, number_wanted) for grad in gradients]
    hexes = [[_val_to_hex(val) for val in part] for part in grad_parts]
    hexes = ["".join(list(z)) for z in zip(*hexes)]
    return ["#" + h for h in hexes]


if __name__ == "__main__":
    colors = ["#FFFFFF", "#E1E1E1", "#303030"]
    chunks = [_chunk_code(c) for c in colors]
    print(chunks)
    vals = [[_hex_to_val(h) for h in chunk] for chunk in chunks]
    print(vals)
    pairs = [z for z in zip(*vals)]
    print("pairs", pairs)
    if len(colors) == 2:
        gradients = [_generate_gradient_two(p[0], p[1]) for p in pairs]
    if len(colors) == 3:
        gradients = [_generate_gradient_three(p[0], p[1], p[2]) for p in pairs]
    print(gradients)
    grad_parts = [_grab_gradient_parts(grad, 4) for grad in gradients]
    print(grad_parts)
    hexes = [[_val_to_hex(val) for val in part] for part in grad_parts]
    print(hexes)
    hexes = ["".join(list(z)) for z in zip(*hexes)]
    print(hexes)
