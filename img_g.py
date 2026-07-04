import math as m

class img:
    def __init__(self, a, b=None):
        if b is None:
            if isinstance(a, img):
                self.img_num = [float(a.real), float(a.imag)]
            elif isinstance(a, list):
                self.img_num = [float(a[0]), float(a[1])]
            else:
                self.img_num = [float(a), 0.0]
        else:
            self.img_num = [float(a), float(b)]

    # --- Addition ---
    def __add__(self, other):
        if isinstance(other, img):
            return img(self.img_num[0] + other.img_num[0],
                       self.img_num[1] + other.img_num[1])
        elif isinstance(other, (int, float)):
            return img(self.img_num[0] + other, self.img_num[1])
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    # --- Subtraction ---
    def __sub__(self, other):
        if isinstance(other, img):
            return img(self.img_num[0] - other.img_num[0],
                       self.img_num[1] - other.img_num[1])
        elif isinstance(other, (int, float)):
            return img(self.img_num[0] - other, self.img_num[1])
        return NotImplemented

    def __rsub__(self, other):
        # This handles: scalar - img_obj
        return img(other) - self

    # --- Multiplication ---
    def __mul__(self, other):
        if isinstance(other, img):
            return img(
                self.img_num[0]*other.img_num[0] - self.img_num[1]*other.img_num[1],
                self.img_num[0]*other.img_num[1] + self.img_num[1]*other.img_num[0]
            )
        elif isinstance(other, (int, float)):
            return img(self.img_num[0]*other, self.img_num[1]*other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    # --- Division ---
    def __truediv__(self, other):
        other_img = img(other)
        denom = other_img.abs2()
        if denom == 0:
            raise ZeroDivisionError("division by zero")
        # Division formula: (z1 * conjugate(z2)) / |z2|^2
        num = self * ~other_img
        return img(num.img_num[0]/denom, num.img_num[1]/denom)

    def __rtruediv__(self, other):
        # This handles: scalar / img_obj
        return img(other) / self

    # --- Power ---
    def __pow__(self, exp):
        # Current logic for integer powers
        if isinstance(exp, int):
            if exp == 0: return img(1, 0)
            result = img(1, 0)
            base = self
            for _ in range(abs(exp)):
                result *= base
            return result if exp > 0 else img(1, 0) / result
        return NotImplemented

    # Note: __rpow__ is complex (requires ln(scalar)). 
    # For now, most users stick to img**int.

    # --- Existing Methods ---
    def __neg__(self):
        return img(-self.img_num[0], -self.img_num[1])

    def conjugate(self):
        return img(self.img_num[0], -self.img_num[1])

    def __invert__(self):
        return self.conjugate()

    def abs2(self):
        return self.img_num[0]**2 + self.img_num[1]**2

    def mod(self):
        return m.sqrt(self.abs2())

    def phase(self):
        return m.atan2(self.img_num[1], self.img_num[0])

    # --- Comparisons (Already work both ways because both sides are implemented) ---
    def __eq__(self, other):
        try:
            other_img = img(other)
            return self.img_num[0] == other_img.img_num[0] and self.img_num[1] == other_img.img_num[1]
        except:
            return False

    def __gt__(self, other):
        return self.mod() > img(other).mod()

    def __lt__(self, other):
        return self.mod() < img(other).mod()

    def __ge__(self, other):
        return self.mod() >= img(other).mod()

    def __le__(self, other):
        return self.mod() <= img(other).mod()

    @property
    def real(self):
        return self.img_num[0]

    @property
    def imag(self):
        return self.img_num[1]

    @staticmethod
    def exp(z):
        a, b = z.img_num[0], z.img_num[1]
        return img(m.exp(a)*m.cos(b), m.exp(a)*m.sin(b))

    def __str__(self):
        sign = "+" if self.img_num[1] >= 0 else "-"
        return f"{self.img_num[0]} {sign} {abs(self.img_num[1])}i"

# --- Testing the new functionality ---
if __name__ == "__main__":
    z = img(2, 3)
    
    print(f"z = {z}")
    print(f"5 + z = {5 + z}")    # Testing __radd__
    print(f"10 - z = {10 - z}")  # Testing __rsub__
    print(f"2 * z = {2 * z}")    # Testing __rmul__
    print(f"1 / z = {1 / z}")    # Testing __rtruediv__
    print(f"5 < z = {5 < z}")    # Testing reflected comparison