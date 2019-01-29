# FG(n)上の楕円曲線で点の足し算，かけ算を行った結果を
# 計算するためのクラス，関数
#
# based on:
# https://github.com/cardwizard/EllipticCurves


from matplotlib import pyplot as plt


# ユーティリティ関数

def modulo_multiply(a, b, mod):
    """
    a * b % modを計算する
    """
    return ((a % mod) * (b % mod)) % mod


def modulo_pow(a, b, mod):
    """
    a^b % modを計算する
    """
    result = 1
    while b:
        result = modulo_multiply(result, a, mod)
        b -= 1
    return result % mod


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)

    g, x, y = egcd(b % a, a)
    return (g, y - (b // a) * x, x)


def modulo_div(a: int, b: int, mod: int) -> int:
    """
    (a / b) % modを計算する
    """
    return modulo_multiply(a, mulinv(b, mod), mod)


def mulinv(b, n):
    g, x, _ = egcd(b, n)

    if g == 1:
        return x % n

    raise Exception("Modular Inverse does not exist")

class EllipticCurve:
    """
    y^2 = x^3 + ax + bで定義される楕円曲線を表現するためのクラス

    """

    def __init__(self, a, b, f_size):
        self.a = a
        self.b = b
        self.field = f_size

    def evaluate_lhs(self, y):
        return modulo_pow(y, 2, self.field)

    def evaluate_rhs(self, x):
        return (modulo_pow(x, 3, self.field) +
                modulo_multiply(x, self.a, self.field) +
                self.b) % self.field

class Point:
    """
    FG(n)上の点を表現するためのクラス
    """
    def __init__(self, curve, x, y):
        self.curve = curve
        self.x = x % self.curve.field
        self.y = y % self.curve.field

    def __neg__(self):
        return Point(self.curve, self.x, -self.y, "{}'".format(self.name))

    def __eq__(self, other):
        return (self.curve, self.x, self.y) == (other.curve, other.x, other.y)

    def __add__(self, Q):
        """
        self+Qを計算する
        """

        if isinstance(Q, Ideal):
            return self

        x_1, y_1, x_2, y_2 = self.x, self.y, Q.x, Q.y

        if (x_1, y_1) == (x_2, y_2):
            if y_1 == 0:
                return Ideal(self.curve)

            numerator = (modulo_multiply(3, modulo_pow(x_1, 2, self.curve.field),
                                         self.curve.field) + self.curve.a) % self.curve.field
            denominator = modulo_multiply(2, y_1, self.curve.field) % self.curve.field

            slope = modulo_div(numerator, denominator, self.curve.field)
        else:
            if x_1 == x_2:
                return Ideal(self.curve)

            numerator = (y_2 - y_1) % self.curve.field
            denominator = (x_2 - x_1) % self.curve.field
            slope = modulo_div(numerator, denominator, self.curve.field)

        x_3 = (modulo_pow(slope, 2, self.curve.field) - x_2 - x_1) % self.curve.field
        y_3 = (modulo_multiply(slope, (x_3 - x_1) % self.curve.field, self.curve.field) + y_1) % self.curve.field

        return Point(self.curve, x_3, -y_3)

    def __mul__(self, n):
        """
        self*nを計算する
        """
        Q = self
        R = self if n & 1 == 1 else Ideal(self.curve)
        i = 2
        while i <= n:
            Q = Q + Q

            if n & i == i:
                R = Q + R
            i = i << 1
        return R


    def __rmul__(self, n: int):
        return self * n

class Ideal(Point):
    def __init__(self, curve):
        self.curve = curve
        self.x = 0
        self.y = 0

    def __str__(self)->str:
        return "Ideal"

    def __neg__(self):
        return self

    def __add__(self, Q):
        return Q


def gfec_plot(a, b, p):
    # 有限体 GF(p) における
    # 楕円曲線 x**3+ax+b-y**2を描画する
    # 楕円曲線上の点を追加するリスト(x, y)を初期化
    xlist = []
    ylist = []
    # x(1-p), y(1-p)の二重ループを実行
    for x in range(1, p+1):
        for y in range(1, p+1):
            if (x**3+a*x+b-y**2) % p == 0:
                # 点(x, y)が曲線上にあった
                xlist.append(x)
                ylist.append(y)
    # リストの点をプロット
    plt.plot(xlist, ylist, ".")


def plot_gfec_points(a, b, p, x, y, m):
    # 有限体 GF(p) における楕円曲線上の点(x, y)を
    # 1からm倍した点を描画する
    
    # グラフのサイズを大きく
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 7
    fig_size[1] = 7
    # 点の座標を保存するリストを初期化
    lx = []
    ly = []
    # 楕円曲線クラスを生成
    ecc = EllipticCurve(a, b, p)
    # 点のクラスを生成
    g = Point(ecc, x, y)
    # 2からm倍までの点を計算，リストに追加する
    for i in range(1, m+1):
        mp = g*i
        lx.append(mp.x)
        ly.append(mp.y)
    # 開始点を描画
    plt.plot(x, y, 'sr')
    # 2からm倍の点を描画
    plt.plot(lx, ly, '--')
    for n in range(len(lx)):
        plt.plot(lx[n], ly[n]+2, 'b', markersize=12, marker='$%d$' % (n+1))
    
    # 楕円曲線上の有限体をグラフ描画
    gfec_plot(a, b, p)
    