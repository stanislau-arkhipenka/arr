def map(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def constrain(x: float, a: float, b: float) -> float:
    assert a <= b
    if x < a:
        return a
    elif x > b:
        return b
    else:
        return x
