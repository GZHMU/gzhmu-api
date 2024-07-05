import os
import numpy as np

pattern_data = os.path.join(os.path.split(__file__)[0], 'data.pk')


def recognize(img: np.ndarray) -> int:
    pattern = np.load(pattern_data, allow_pickle=True)

    left = 0
    max_rate = 0
    for i, n in enumerate(pattern['left_operand']):
        score = 0
        total = 0
        for r, cols in n.items():
            for c in cols:
                score += sum(img[r,c]) < 765
            total += len(cols)
        rate = score / total
        if rate > max_rate:
            left = i + 1
            if rate == 1:
                break
            max_rate = rate

    sign = ''
    max_rate = 0
    for s, n in pattern['sign'].items():
        score = 0
        total = 0
        for r, cols in n.items():
            for c in cols:
                score += sum(img[r,c]) < 765
            total += len(cols)
        rate = score / total
        if rate > max_rate:
            sign = s
            if rate == 1:
                break
            max_rate = rate

    right = 0
    max_rate = 0
    for i, n in enumerate(pattern['left_operand']):
        score = 0
        total = 0
        for r, cols in n.items():
            for c in cols:
                score += sum(img[r,c+pattern['gap']]) < 765
            total += len(cols)
        rate = score / total
        if rate > max_rate:
            right = i + 1
            if rate == 1:
                break
            max_rate = rate

    if sign == 'add':
        return left + right
    elif sign == 'minus':
        return left - right
    elif sign == 'multiply':
        return left * right
    else:
        return 0
