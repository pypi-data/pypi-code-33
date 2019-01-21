#! /usr/bin/env python

import numpy


class Quaternions:
    spaceGroups = {}
    spaceGroups["1"] = ["P 1",
                        "A 1",
                        "B 1",
                        "C 1",
                        "I 1",
                        "F 1"]

    spaceGroups["2"] = ["P 1 2 1",
                        "P 1 21 1",
                        "C 1 2 1",
                        "I 1 2 1"]

    spaceGroups["222"] = ["P 2 2 2",
                          "P 2 2 21",
                          "P 21 2 2",
                          "P 2 21 2",
                          "P 21 21 2",
                          "P 2 21 21",
                          "P 21 2 21",
                          "P 21 21 21",
                          "C 2 2 21",
                          "C 2 2 2",
                          "A 2 2 2",
                          "B 2 2 2"
                          "B 2 21 2",
                          "A 21 2 2",
                          "F 2 2 2",
                          "I 2 2 2",
                          "I 21 21 21"]

    spaceGroups["4"] = ["P 4", \
                        "P 41", \
                        "P 42", \
                        "P 43", \
                        "I 4", \
                        "I 41"]

    spaceGroups["422"] = ["P 4 2 2", \
                          "P 4 21 2", \
                          "P 41 2 2", \
                          "P 41 21 2", \
                          "P41212", \
                          "P 42 2 2", \
                          "P4222", \
                          "P 42 21 2", \
                          "P 43 2 2", \
                          "P43212", \
                          "P 43 21 2", \
                          "I 4 2 2", \
                          "I 41 2 2"]

    spaceGroups["3"] = ["P 3", \
                        "P 31", \
                        "P 32", \
                        "R 3", \
                        "H 3"]

    spaceGroups["312"] = ["P 3 1 2", \
                          "P 31 1 2", \
                          "P 32 1 2"]

    spaceGroups["321"] = ["P 3 2 1", \
                          "P 31 2 1", \
                          "P 32 2 1"]

    spaceGroups["32"] = ["R 3 2", \
                         "H 3 2"]

    spaceGroups["6"] = ["P 6",
                        "P 61",
                        "P 65",
                        "P 62",
                        "P 64",
                        "P 63"]

    spaceGroups["622"] = ["P 6 2 2", \
                          "P 61 2 2", \
                          "P 65 2 2", \
                          "P 62 2 2", \
                          "P 64 2 2", \
                          "P 63 2 2"]

    spaceGroups["23"] = ["P 2 3", \
                         "F 2 3", \
                         "I 2 3", \
                         "P 21 3", \
                         "I 21 3"]

    spaceGroups["432"] = ["P 4 3 2", \
                          "P 42 3 2", \
                          "F 4 3 2", \
                          "F 41 3 2", \
                          "I 4 3 2", \
                          "P 43 3 2", \
                          "P 41 3 2", \
                          "I 41 3 2"]

    origins = {}
    origins["P 21 21 21"] = {1: [0.0, 0.0, 0.0], 2: [0.0, 0.0, 0.5], 3: [0.0, 0.5, 0.0], 4: [0.5, 0.0, 0.0],
                             5: [0.0, 0.5, 0.5], \
                             6: [0.5, 0.0, 0.5], 7: [0.5, 0.5, 0.0], 8: [0.5, 0.5, 0.5]}

    matricesTra = {}
    matricesTra["P 21 21 21"] = {1: [0, 0, 0], \
                                 2: [0.5, 0.0, 0.5], \
                                 3: [0.0, 0.5, 0.5], \
                                 4: [0.5, 0.5, 0.0]}

    matricesTra["P 1 21 1"] = {1: [0, 0, 0], \
                               2: [0.0, 0.5, 0.0]}

    matricesRot = {}
    matricesRot["1"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}

    matricesRot["2"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                        2: [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]}

    matricesRot["222"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],     # x, y, z
                          2: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]],   # -x, -y, z
                          3: [[-1, 0, 0], [0, 1, 0], [0, 0, -1]],   # -x, y, -z
                          4: [[1, 0, 0], [0, -1, 0], [0, 0, -1]]}   # x, -y, -z

    matricesRot["4"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                        2: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]], \
                        3: [[0, -1, 0], [1, 0, 0], [0, 0, 1]], \
                        4: [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]}

    matricesRot["422"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],     # x, y, z
                          2: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]],   # -x, -y, z
                          3: [[0, -1, 0], [1, 0, 0], [0, 0, 1]],    # -y, x, z
                          4: [[0, 1, 0], [-1, 0, 0], [0, 0, 1]],    # y, -x, z
                          5: [[-1, 0, 0], [0, 1, 0], [0, 0, -1]],   # -x, y, -z
                          6: [[1, 0, 0], [0, -1, 0], [0, 0, -1]],   # x, -y, -z
                          7: [[0, 1, 0], [1, 0, 0], [0, 0, -1]],    # y, x, -z
                          8: [[0, -1, 0], [-1, 0, 0], [0, 0, -1]]}  # -y, -x, -z

    matricesRot["3"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                        2: [[0, -1, 0], [1, -1, 0], [0, 0, 1]], \
                        3: [[-1, 1, 0], [-1, 0, 0], [0, 0, 1]]}

    matricesRot["312"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                          2: [[0, -1, 0], [1, -1, 0], [0, 0, 1]], \
                          3: [[-1, 1, 0], [-1, 0, 0], [0, 0, 1]], \
                          4: [[0, -1, 0], [-1, 0, 0], [0, 0, -1]], \
                          5: [[-1, 1, 0], [0, 1, 0], [0, 0, -1]], \
                          6: [[1, 0, 0], [1, -1, 0], [0, 0, -1]]}

    matricesRot["321"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                          2: [[0, -1, 0], [1, -1, 0], [0, 0, 1]], \
                          3: [[-1, 1, 0], [-1, 0, 0], [0, 0, 1]], \
                          4: [[0, 1, 0], [1, 0, 0], [0, 0, -1]], \
                          5: [[1, -1, 0], [0, -1, 0], [0, 0, -1]], \
                          6: [[-1, 0, 0], [-1, 1, 0], [0, 0, -1]]}

    matricesRot["32"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                         2: [[0, -1, 0], [1, -1, 0], [0, 0, 1]], \
                         3: [[-1, 1, 0], [-1, 0, 0], [0, 0, 1]], \
                         4: [[0, 1, 0], [1, 0, 0], [0, 0, -1]], \
                         5: [[1, -1, 0], [0, -1, 0], [0, 0, -1]], \
                         6: [[-1, 0, 0], [-1, 1, 0], [0, 0, -1]]}

    matricesRot["6"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],    # x, y, z
                        2: [[0, -1, 0], [1, -1, 0], [0, 0, 1]],  # -y, x-y, z
                        3: [[-1, 1, 0], [-1, 0, 0], [0, 0, 1]],  # -x+y, -x, z
                        4: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]],  # -x, -y, z
                        5: [[0, 1, 0], [-1, 1, 0], [0, 0, 1]],   # y, -x+y, z
                        6: [[1, -1, 0], [1, 0, 0], [0, 0, 1]]}   # x-y, x, z

    matricesRot["622"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                          2: [[0, -1, 0], [1, -1, 0], [0, 0, 1]], \
                          3: [[-1, 1, 0], [-1, 0, 0], [0, 0, 1]], \
                          4: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]], \
                          5: [[0, 1, 0], [-1, 1, 0], [0, 0, 1]], \
                          6: [[1, -1, 0], [1, 0, 0], [0, 0, 1]], \
                          7: [[0, 1, 0], [1, 0, 0], [0, 0, -1]], \
                          8: [[1, -1, 0], [0, -1, 0], [0, 0, -1]], \
                          9: [[-1, 0, 0], [-1, 1, 0], [0, 0, -1]], \
                          10: [[0, -1, 0], [-1, 0, 0], [0, 0, -1]],
                          11: [[-1, 1, 0], [0, 1, 0], [0, 0, -1]], \
                          12: [[1, 0, 0], [1, -1, 0], [0, 0, -1]]}

    matricesRot["23"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                         2: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]], \
                         3: [[-1, 0, 0], [0, 1, 0], [0, 0, -1]], \
                         4: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], \
                         5: [[0, 0, 1], [1, 0, 0], [0, 1, 0]], \
                         6: [[0, 0, 1], [-1, 0, 0], [0, -1, 0]], \
                         7: [[0, 0, -1], [-1, 0, 0], [0, 1, 0]], \
                         8: [[0, 0, -1], [1, 0, 0], [0, -1, 0]], \
                         9: [[0, 1, 0], [0, 0, 1], [1, 0, 0]], \
                         10: [[0, -1, 0], [0, 0, 1], [-1, 0, 0]], \
                         11: [[0, 1, 0], [0, 0, -1], [-1, 0, 0]], \
                         12: [[0, -1, 0], [0, 0, -1], [1, 0, 0]]}

    matricesRot["432"] = {1: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], \
                          2: [[-1, 0, 0], [0, -1, 0], [0, 0, 1]], \
                          3: [[-1, 0, 0], [0, 1, 0], [0, 0, -1]], \
                          4: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], \
                          5: [[0, 0, 1], [1, 0, 0], [0, 1, 0]], \
                          6: [[0, 0, 1], [-1, 0, 0], [0, -1, 0]], \
                          7: [[0, 0, -1], [-1, 0, 0], [0, 1, 0]], \
                          8: [[0, 0, -1], [1, 0, 0], [0, -1, 0]], \
                          9: [[0, 1, 0], [0, 0, 1], [1, 0, 0]], \
                          10: [[0, -1, 0], [0, 0, 1], [-1, 0, 0]], \
                          11: [[0, 1, 0], [0, 0, -1], [-1, 0, 0]], \
                          12: [[0, -1, 0], [0, 0, -1], [1, 0, 0]], \
                          13: [[0, 1, 0], [1, 0, 0], [0, 0, -1]], \
                          14: [[0, -1, 0], [-1, 0, 0], [0, 0, -1]], \
                          15: [[0, 1, 0], [-1, 0, 0], [0, 0, 1]], \
                          16: [[0, -1, 0], [1, 0, 0], [0, 0, 1]], \
                          17: [[1, 0, 0], [0, 0, 1], [0, -1, 0]], \
                          18: [[-1, 0, 0], [0, 0, 1], [0, 1, 0]], \
                          19: [[-1, 0, 0], [0, 0, -1], [0, -1, 0]], \
                          20: [[1, 0, 0], [0, 0, -1], [0, 1, 0]], \
                          21: [[0, 0, 1], [0, 1, 0], [-1, 0, 0]], \
                          22: [[0, 0, 1], [0, -1, 0], [1, 0, 0]], \
                          23: [[0, 0, -1], [0, 1, 0], [1, 0, 0]], \
                          24: [[0, 0, -1], [0, -1, 0], [-1, 0, 0]]}

    quaterRotaz = {}

    def __init__(self):
        for key, value in self.matricesRot.iteritems():
            for k, v in value.iteritems():
                quat = self.convertRotMatrixToQuaternion2(v)
                if key not in self.quaterRotaz.keys():
                    self.quaterRotaz[key] = {k: quat}
                    # print key,k,quat
                else:
                    (self.quaterRotaz[key])[k] = quat
                    # print key,k,quat

    # @staticmethod
    def createQuaternion(self, rotationAngle, vect):
        halfangle = self.DegToRad(rotationAngle) / 2.0
        myCosine = numpy.cos(halfangle)
        mySine = numpy.sin(halfangle)

        q3 = myCosine
        q0 = vect[0] * mySine
        q1 = vect[1] * mySine
        q2 = vect[2] * mySine
        qu = [q0, q1, q2, q3]

        return self.NormalizeQuaternion(qu)

    # @staticmethod
    def DegToRad(self, angle):
        return (angle * 2 * numpy.pi) / 360.0

    def getLaueSimmetry(self, spaceGr):
        for key, value in self.spaceGroups.iteritems():
            if spaceGr in value:
                return key

    # @staticmethod
    def NormalizeQuaternion(self, q):
        valueSquared = ((q[3] ** 2) + (q[0] ** 2) + (q[1] ** 2) + (q[2] ** 2))
        value = numpy.sqrt(valueSquared)
        q[0] /= value
        q[1] /= value
        q[2] /= value
        q[3] /= value

        return q

    # @staticmethod
    def convertEulerToQuaternion2(self, angle1, angle2, angle3, standard):
        """
                James Diebel 2006
        """
        if len(standard) != 3:
            raise Exception("Standard not existent")
        if standard[0] not in ["x", "y", "z"] or standard[1] not in ["x", "y", "z"] or standard[2] not in ["x", "y",
                                                                                                           "z"]:
            raise Exception("Standard not existent")

        halfangle = self.DegToRad(angle1) / 2.0
        c1 = numpy.cos(halfangle)
        s1 = mySine = numpy.sin(halfangle)

        halfangle = self.DegToRad(angle2) / 2.0
        c2 = numpy.cos(halfangle)
        s2 = mySine = numpy.sin(halfangle)

        halfangle = self.DegToRad(angle3) / 2.0
        c3 = numpy.cos(halfangle)
        s3 = mySine = numpy.sin(halfangle)

        q1 = (c1 * c2 * c3) - (s1 * c2 * s3)
        q2 = (-1 * c1 * s2 * s3) + (s1 * c3 * s2)
        q3 = (c1 * c3 * s2) + (s1 * s2 * s3)
        q4 = (c1 * c2 * s3) + (c2 * c3 * s1)
        op = [q4, q1, q2, q3]
        # print "Obtained",op

        return self.NormalizeQuaternion(op)

    # @staticmethod
    def convertEulerToQuaternion(self, angle1, angle2, angle3, standard):
        """

        """
        if len(standard) != 3:
            raise Exception("Standard not existent")
        if standard[0] not in ["x", "y", "z"] or standard[1] not in ["x", "y", "z"] or standard[2] not in ["x", "y",
                                                                                                           "z"]:
            raise Exception("Standard not existent")

        # ra1 = DegToRad(angle1)
        # ra2 = DegToRad(angle2)
        # ra3 = DegToRad(angle3)

        firQuat = [0.0, 0.0, 0.0, 0.0]
        secQuat = [0.0, 0.0, 0.0, 0.0]
        terQuat = [0.0, 0.0, 0.0, 0.0]

        if standard[0] == "x":
            firQuat = self.createQuaternion(angle1, [1, 0, 0])
        elif standard[0] == "y":
            firQuat = self.createQuaternion(angle1, [0, 1, 0])
        elif standard[0] == "z":
            firQuat = self.createQuaternion(angle1, [0, 0, 1])

        if standard[1] == "x":
            secQuat = self.createQuaternion(angle2, [1, 0, 0])
        elif standard[1] == "y":
            secQuat = self.createQuaternion(angle2, [0, 1, 0])
        elif standard[1] == "z":
            secQuat = self.createQuaternion(angle2, [0, 0, 1])

        if standard[2] == "x":
            terQuat = self.createQuaternion(angle3, [1, 0, 0])
        elif standard[2] == "y":
            terQuat = self.createQuaternion(angle3, [0, 1, 0])
        elif standard[2] == "z":
            terQuat = self.createQuaternion(angle3, [0, 0, 1])

        # print "First: ",firQuat
        # print "Second: ",secQuat
        # print "Third: ",terQuat

        # end = self.QuaternionProduct(firQuat,secQuat)
        # end = self.QuaternionProduct(end,terQuat)
        op = self.QuaternionProduct(terQuat, secQuat)
        op = self.QuaternionProduct(op, firQuat)
        # print "3*2*1: ",op
        return self.NormalizeQuaternion(op)

    def QuaternionProduct(self, q1, q2):
        """
        qout = [0.0,0.0,0.0,0.0]
        qout[3] = (q1[3]*q2[3]) - (q1[0]*q2[0]) - (q1[1]*q2[1]) - (q1[2]*q2[2])
        qout[0] = (q1[3]*q2[0]) + (q1[0]*q2[3]) + (q1[1]*q2[2]) - (q1[2]*q2[1])
        qout[1] = (q1[3]*q2[1]) + (q1[1]*q2[3]) - (q1[0]*q2[2]) + (q1[2]*q2[0])
        qout[2] = (q1[3]*q2[2]) + (q1[2]*q2[3]) + (q1[0]*q2[1]) - (q1[1]*q2[0])
        """
        qout = [0.0, 0.0, 0.0, 0.0]
        qout[3] = (q1[3] * q2[3]) - (q1[0] * q2[0]) - (q1[1] * q2[1]) - (q1[2] * q2[2])
        qout[0] = (q1[0] * q2[3]) + (q1[3] * q2[0]) - (q1[2] * q2[1]) + (q1[1] * q2[2])
        qout[1] = (q1[1] * q2[3]) + (q1[2] * q2[0]) + (q1[3] * q2[1]) - (q1[0] * q2[2])
        qout[2] = (q1[2] * q2[3]) - (q1[1] * q2[0]) + (q1[0] * q2[1]) + (q1[3] * q2[2])
        return qout

    def PointQuaternionProd(self, pin, q):
        pout = [0.0, 0.0, 0.0, 0.0]
        pout[3] = 0
        pout[0] = (pin[3] * q[0]) + (pin[0] * q[3]) + (pin[1] * q[2]) - (pin[2] * q[1])
        pout[1] = (pin[3] * q[1]) + (pin[1] * q[3]) - (pin[0] * q[2]) + (pin[2] * q[0])
        pout[2] = (pin[3] * q[2]) + (pin[2] * q[3]) + (pin[0] * q[1]) - (pin[1] * q[0])
        return pout

    def signOfQuaternionComponents(self, q):
        s0 = 0
        s1 = 0
        s2 = 0
        s3 = 0
        if q[0] >= 0:
            s0 = 1
        else:
            s0 = -1

        if q[1] >= 0:
            s1 = 1
        else:
            s1 = -1

        if q[2] >= 0:
            s2 = 1
        else:
            s2 = -1

        if q[3] >= 0:
            s3 = 1
        else:
            s3 = -1

        return [s0, s1, s2, s3]

    def RotateQuaternion(self, quat, qRot):
        qAxisConjugate = self.QuaternionConjugate(qRot)
        tmpQ = self.QuaternionProduct(qRot, quat)
        adtn = self.QuaternionProduct(tmpQ, qAxisConjugate)
        return self.NormalizeQuaternion(adtn)

    def QuaternionConjugate(self, qin):
        qout = [0.0, 0.0, 0.0, 0.0]
        qout[3] = float(qin[3])
        qout[0] = -1.0 * qin[0]
        qout[1] = -1.0 * qin[1]
        qout[2] = -1.0 * qin[2]
        return qout

    def QuaternionDotProduct(self, q1, q2):
        dot = (q1[3] * q2[3]) + (q1[0] * q2[0]) + (q1[1] * q2[1]) + (q1[2] * q2[2])
        return dot

    def QuaternionInverse(self, qin):
        qcon = self.QuaternionConjugate(qin)
        qsquare = self.QuaternionDotProduct(qin, qin)
        return self.QuaternionVsScalarDivision(qcon, qsquare)

    def QuaternionVsScalarDivision(self, q1, number):
        number = float(number)
        return [q1[0] / number, q1[1] / number, q1[2] / number, q1[3] / number]

    def QuaternionDivision(self, q1, q2):
        # url: http://www.mathworks.es/es/help/aeroblks/quaterniondivision.html
        qout = [0.0, 0.0, 0.0, 0.0]
        qout[3] = ((q1[3] * q2[3]) + (q1[0] * q2[0]) + (q1[1] * q2[1]) + (q1[2] * q2[2])) / (
        (q2[3] ** 2) + (q2[0] ** 2) + (q2[1] ** 2) + (q2[2] ** 2))  # angle
        qout[0] = ((q2[3] * q1[0]) - (q2[0] * q1[3]) - (q2[1] * q1[2]) + (q2[2] * q1[1])) / (
        (q2[3] ** 2) + (q2[0] ** 2) + (q2[1] ** 2) + (q2[2] ** 2))  # i component
        qout[1] = ((q2[3] * q1[1]) + (q2[0] * q1[2]) - (q2[1] * q1[3]) - (q2[2] * q1[0])) / (
        (q2[3] ** 2) + (q2[0] ** 2) + (q2[1] ** 2) + (q2[2] ** 2))  # j component
        qout[2] = ((q2[3] * q1[2]) - (q2[0] * q1[1]) + (q2[1] * q1[0]) - (q2[2] * q1[3])) / (
        (q2[3] ** 2) + (q2[0] ** 2) + (q2[1] ** 2) + (q2[2] ** 2))  # k component

        return qout

    def convertQuaternionToMatrix(self, q):
        w = q[3]
        x = q[0]
        y = q[1]
        z = q[2]

        R = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        R[0][0] = 1 - (2 * y ** 2) - (2 * z ** 2)
        R[0][1] = 2 * x * y - 2 * w * z
        R[0][2] = 2 * x * z + 2 * w * y
        R[1][0] = 2 * x * y + 2 * w * z
        R[1][1] = 1 - (2 * x ** 2) - (2 * z ** 2)
        R[1][2] = 2 * y * z - 2 * w * x
        R[2][0] = 2 * x * z - 2 * w * y
        R[2][1] = 2 * y * z + 2 * w * x
        R[2][2] = 1 - (2 * x ** 2) - (2 * y ** 2)
        return R

    def convertRotMatrixToQuaternion2(self, mat):
        tr = mat[0][0] + mat[1][1] + mat[2][2]
        if (tr > 0):
            S = numpy.sqrt(tr + 1.0) * 2  # S=4*qw
            qw = 0.25 * S
            qx = (mat[2][1] - mat[1][2]) / S
            qy = (mat[0][2] - mat[2][0]) / S
            qz = (mat[1][0] - mat[0][1]) / S
        elif ((mat[0][0] > mat[1][1]) and (mat[0][0] > mat[2][2])):
            S = numpy.sqrt(1.0 + mat[0][0] - mat[1][1] - mat[2][2]) * 2  # // S=4*qx
            qw = (mat[2][1] - mat[1][2]) / S
            qx = 0.25 * S
            qy = (mat[0][1] + mat[1][0]) / S
            qz = (mat[0][2] + mat[2][0]) / S
        elif (mat[1][1] > mat[2][2]):
            S = numpy.sqrt(1.0 + mat[1][1] - mat[0][0] - mat[2][2]) * 2  # // S=4*qy
            qw = (mat[0][2] - mat[2][0]) / S
            qx = (mat[0][1] + mat[1][0]) / S
            qy = 0.25 * S
            qz = (mat[1][2] + mat[2][1]) / S
        else:
            S = numpy.sqrt(1.0 + mat[2][2] - mat[0][0] - mat[1][1]) * 2  # // S=4*qz
            qw = (mat[1][0] - mat[0][1]) / S
            qx = (mat[0][2] + mat[2][0]) / S
            qy = (mat[1][2] + mat[2][1]) / S
            qz = 0.25 * S

        return [qx, qy, qz, qw]

    def convertRotMatrixToQuaternion(self, mat):
        T = mat[0][0] + mat[1][1] + mat[2][2]
        if T > 0:
            S = 0.5 / numpy.sqrt(T)
            W = 0.25 / S
            X = (mat[2][1] - mat[1][2]) * S
            Y = (mat[0][2] - mat[2][0]) * S
            Z = (mat[1][0] - mat[0][1]) * S
            return [X, Y, Z, W]
        else:
            firstColumn = False
            secondColumn = False
            thirdColumn = False
            if mat[0][0] >= mat[1][1]:
                if mat[0][0] >= mat[2][2]:
                    firstColumn = True
                    secondColumn = False
                    thirdColumn = False
                else:
                    firstColumn = False
                    secondColumn = False
                    thirdColumn = True
            elif mat[1][1] >= mat[2][2]:
                firstColumn = False
                secondColumn = True
                thirdColumn = False
            else:
                firstColumn = False
                secondColumn = False
                thirdColumn = True

            mr = mat
            if firstColumn:
                S = numpy.sqrt(mr[0][0] - mr[1][1] - mr[2][2]) * 2
                Qx = 0.5 / S
                Qy = (mr[0][1] + mr[1][0]) / S
                Qz = (mr[0][2] + mr[2][0]) / S
                Qw = (mr[1][2] + mr[2][1]) / S
            elif secondColumn:
                S = numpy.sqrt(mr[1][1] - mr[0][0] - mr[2][2]) * 2
                Qx = (mr[0][1] + mr[1][0]) / S
                Qy = 0.5 / S
                Qz = (mr[1][2] + mr[2][1]) / S
                Qw = (mr[0][2] + mr[2][0]) / S
            elif thirdColumn:
                S = numpy.sqrt(mr[2][2] - mr[0][0] - mr[1][1]) * 2
                Qx = (mr[0][2] + mr[2][0]) / S
                Qy = (mr[1][2] + mr[2][1]) / S
                Qz = 0.5 / S
                Qw = (mr[0][1] + mr[1][0]) / S

            return [Qx, Qy, Qz, Qw]
