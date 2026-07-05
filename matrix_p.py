# matrix_p.py - ADD MISSING METHODS
import random
import math
try:
    from img_g import img
except ModuleNotFoundError:
    from .img_g import img

class Matrix:
    _op_priority = 11.0
    def __init__(self, mat):
        if not mat or not mat[0]:
            raise ValueError("matrix cannot be empty")
        self.matrix = mat
        self.no_of_rows = len(mat)
        self.no_of_columns = len(mat[0])

    @staticmethod
    def matrix(no_of_rows, no_of_columns):
        matrix = []
        for _ in range(no_of_rows):
            row = []
            while len(row) < no_of_columns:
                try:
                    element = int(input("enter element:"))
                    row.append(element)
                except:
                    print("ENTER ONLY NUMBERS!!!")
            matrix.append(row)
        return Matrix(matrix)
    
    def copy(self):
        """Create a deep copy of the matrix"""
        copied_matrix = [row[:] for row in self.matrix]
        return Matrix(copied_matrix)

    def order(self):
        print (f"{self.no_of_rows} X {self.no_of_columns}")
        return (self.no_of_rows,self.no_of_columns)
   
    def max_size_element(self):
        max_ = 1
        for i in range(self.no_of_rows):
            for j in range(self.no_of_columns):
                temp = len(str(self.matrix[i][j]))
                if temp > max_:
                    max_ = temp
        return max_
   
    def show(self, identity="Matrix"):
        max_ = self.max_size_element()
        print()
        if identity == "Matrix":
            print(f"{identity}:")
        else:
            print(f"{identity}=")

        for i in range(self.no_of_rows):
            print("|", end=" ")
            for j in range(self.no_of_columns):
                print(f"{str(self.matrix[i][j]):>{max_}}", end=" ")
            print("|")

    # ======================================================= basic operations ======================================================
    def __add__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        if not self.order_check(other):
            raise ValueError("Matrices must have equal dimensions")
        sum_matrix = []
        for i in range(len(self.matrix)):
            sum_matrix.append(Matrix.row_sum(self.matrix[i], other.matrix[i]))
        return Matrix(sum_matrix)

    def __sub__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        if not self.order_check(other):
            raise ValueError("Matrices must have equal dimensions")
        sub_matrix = []
        for i in range(len(self.matrix)):
            sub_matrix.append(Matrix.row_sub(self.matrix[i], other.matrix[i]))
        return Matrix(sub_matrix)
   
    def __mul__(self, other):
        if isinstance(other, Matrix):
            if len(self.matrix[0]) == len(other.matrix):
                matrix = []
                temp_row = [[]]
                for j in range(len(other.matrix[0])):
                    for i in range(len(other.matrix)):
                        temp_row[j].append(other.matrix[i][j])
                    temp_row.append([])
                temp_row.pop()

                for i in range(len(self.matrix)):
                    temp = []
                    for j in range(len(temp_row)):
                        temp.append(Matrix.row_mul(self.matrix[i], temp_row[j]))
                    matrix.append(temp)
                return Matrix(matrix)
            else:
                print("cannot multiply these matrix")
                return f"cannot multiply these matrix"
               
        elif isinstance(other, (int, float, img)):
            matrix = []
            for i in range(len(self.matrix)):
                temp = []
                for j in range(len(self.matrix[0])):
                    temp.append(self.matrix[i][j] * other)
                matrix.append(temp)
            return Matrix(matrix)
       
        else:
            return NotImplemented
   
    def __rmul__(self, other):
        return self.__mul__(other)
   
    def __pow__(self, n):
        if not isinstance(n, int):
            raise TypeError("only integer allowed")
        if self.no_of_rows != self.no_of_columns:
            raise ValueError("power only defined for square matrices")

        if n < 0:
            return (self.inverse()) ** (-n)
        elif n == 0:
            return Matrix.identity_matrix(self.no_of_rows)
        else:
            product = self
            for _ in range(n - 1):
                product = product * self
            return product

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        if self.no_of_rows != other.no_of_rows or self.no_of_columns != other.no_of_columns:
            return False

        condition = True
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j] != other.matrix[i][j]:
                    condition = False
        return condition
   
    def __xor__(self, other):  # Element-wise product
        if self.no_of_columns != other.no_of_columns or self.no_of_rows != other.no_of_rows:
            raise ValueError("Matrices must have equal dimensions")
        matrix = []
        for i in range(self.no_of_rows):
            row = []
            for j in range(self.no_of_columns):
                row.append(self.matrix[i][j] * other.matrix[i][j])
            matrix.append(row)
        return Matrix(matrix)

    def trace(self):
        if self.no_of_columns != self.no_of_rows:
            raise ValueError("Trace only defined for square matrices")
        total = img(0, 0)
        for i in range(self.no_of_rows):
            total += self.matrix[i][i]
        return total

    def order_check(self, other):
        return (len(self.matrix) == len(other.matrix)
                and len(self.matrix[0]) == len(other.matrix[0]))
   
    # ======================================================= STATIC METHODS ======================================================
    @staticmethod
    def row_sum(l1, l2):
        return [l1[i] + l2[i] for i in range(len(l1))]

    @staticmethod
    def row_sub(l1, l2):
        return [l1[i] - l2[i] for i in range(len(l1))]

    @staticmethod
    def row_mul(l1, l2):
        total = img(0, 0)
        for i in range(len(l1)):
            total += l1[i] * l2[i]
        return total

    # ======================================================= INDEXING SUPPORT ======================================================
    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            i, j = key
            return self.matrix[i][j]
        elif isinstance(key, tuple) and len(key) == 1:
            i = key[0]
            return self.matrix[i]
        elif isinstance(key, int):
            return self.matrix[key]
        raise IndexError("Use matrix[i,j] or matrix[i]")
   
    def __setitem__(self, key, value):
        """Allow setting matrix elements with matrix[i,j] = value"""
        if isinstance(key, tuple) and len(key) == 2:
            i, j = key
            self.matrix[i][j] = value
        else:
            raise IndexError("Use matrix[i,j] = value")
   
    def value(self):
        if self.no_of_rows == 1 and self.no_of_columns == 1:
            return self.matrix[0][0]
        raise ValueError("value() only for 1x1 matrices")

    # ======================================================= EDIT METHODS =========================================================
    def edit_element(self, row, column, new_value):
        self.matrix[row-1][column-1] = new_value
   
    def edit_row(self, row, new_row):
        if len(new_row) == self.no_of_columns:
            self.matrix[row-1] = new_row
        else:
            print("number of columns does not match the matrix!!!")

    def edit_column(self, column, new_column):
        if len(new_column) == self.no_of_rows:
            for i in range(self.no_of_rows):
                self.matrix[i][column-1] = new_column[i]
        else:
            print("the number of rows does not match the matrix")

    # ======================================================= TRANSPOSE ============================================================
    def transpose(self, type="modify"):
        t_matrix = []
        for i in range(self.no_of_columns):
            row = []
            for j in range(self.no_of_rows):
                row.append(self.matrix[j][i])
            t_matrix.append(row)

        if type == "new":
            return Matrix(t_matrix)
        elif type == "modify":
            self.matrix = t_matrix
            self.no_of_rows, self.no_of_columns = self.no_of_columns, self.no_of_rows
        else:
            print("not a valid type")
            return "not a valid type"

    # ======================================================= DETERMINANT ==========================================================
    def det(self):
        if self.no_of_rows != self.no_of_columns:
            print("Not a square matrix")
            return None

        def determinant(matrix):
            n = len(matrix)
            if n == 1:
                return matrix[0][0]
            if n == 2:
                return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0])
            det_val = img(0, 0)
            for col in range(n):
                submatrix = [row[:col] + row[col+1:] for row in matrix[1:]]
                det_val += ((-1) ** col) * matrix[0][col] * determinant(submatrix)
            return det_val
        return determinant(self.matrix)

    # ======================================================= ADJOINT/INVERSE =======================================================
    def adjoint(self):
        matrix = []
        for i in range(self.no_of_rows):
            row = []
            for j in range(self.no_of_columns):
                cofactor_ = Matrix.cofactor(i, j, self.matrix)
                row.append(cofactor_)
            matrix.append(row)
        return Matrix(matrix).transpose("new")
   
    def inverse(self):
        det_val = self.det()
        if det_val == 0:
            raise ValueError("Matrix is singular (determinant = 0)")
        return self.adjoint() * (img(1,0) / det_val)

    @staticmethod
    def cofactor(m, n, matrix):
        row_count = len(matrix)
        column_count = len(matrix[0])

        if row_count != column_count:
            print("not a square matrix - cofactor")
            return None

        if row_count == 1:
            return img(1, 0)

        cofactor_matrix = []
        for i in range(row_count):
            if i == m:
                continue
            row = []
            for j in range(column_count):
                if j == n:
                    continue
                row.append(matrix[i][j])
            cofactor_matrix.append(row)

        bc = Matrix(cofactor_matrix)
        return bc.det() * ((-1) ** (m + n))

    def orthogonal_check(self, tol=1e-9):
        if self.no_of_rows != self.no_of_columns:
            return False
        product = self * self.transpose("new")
        identity = Matrix.identity_matrix(self.no_of_rows)
       
        for i in range(self.no_of_rows):
            for j in range(self.no_of_columns):
                if abs((product[i,j] - identity[i,j]).mod()) > tol:
                    return False
        return True

    # ======================================================= RANDOM & EXTRAS ======================================================
    @staticmethod
    def is_identity(a, tol=1e-9):
        rows = len(a.matrix)
        cols = len(a.matrix[0])

        if rows != cols:
            print("matrix is not square matrix")
            return False

        for i in range(rows):
            for j in range(cols):
                val = a.matrix[i][j]
                if not isinstance(val, img):
                    val = img(val, 0)

                if i == j:
                    if abs(val.real - 1) > tol or abs(val.imag) > tol:
                        return False
                else:
                    if abs(val.real) > tol or abs(val.imag) > tol:
                        return False
        return True

    def conjugate_transpose(self):
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        result = [[img(0,0) for _ in range(rows)] for _ in range(cols)]

        for i in range(rows):
            for j in range(cols):
                val = self.matrix[i][j]
                if isinstance(val, img):
                    result[j][i] = val.conjugate()
                else:
                    result[j][i] = img(val, 0)

        return Matrix(result)

    def unitary_check(self):
        U_dagger = self.conjugate_transpose()
        product = U_dagger * self
        return Matrix.is_identity(product)

    @staticmethod
    def random(m, n, range_=(0, 10)):
        matrix = []
        for _ in range(m):
            row = []
            for _ in range(n):
                row.append(random.randint(range_[0], range_[1]))
            matrix.append(row)
        return Matrix(matrix)
    
    @staticmethod
    def zeros(m, n):
        """Create an m x n zero matrix"""
        mat = []
        for i in range(m):
            row = []
            for j in range(n):
                row.append(img(0, 0))  # Use img(0,0) for complex zeros
            mat.append(row)
        return Matrix(mat)
   
    @staticmethod
    def check_zero_matrix(l):
        for i in l:
            if i != 0:
                return False
        return True

    @staticmethod
    def rearrange(matrix_1):
        leading_nonzeros_list = []

        for i in range(matrix_1.no_of_rows):
            if Matrix.check_zero_matrix(matrix_1.matrix[i]):
                leading_nonzeros_list.append((i, float('inf')))
            else:
                for j in range(matrix_1.no_of_columns):
                    if matrix_1.matrix[i][j] != 0:
                        leading_nonzeros_list.append((i, j))
                        break

        leading_nonzeros_list.sort(key=lambda x: x[1])
        rearranged_matrix = [matrix_1.matrix[row_index] for (row_index, _) in leading_nonzeros_list]

        return Matrix(rearranged_matrix)

    def tensor(self, other):
        tensor_matrix = []
        for i in range(self.no_of_rows):
            for io in range(other.no_of_rows):
                row = []
                for j in range(self.no_of_columns):
                    for jo in range(other.no_of_columns):
                        row.append(self.matrix[i][j] * other.matrix[io][jo])
                tensor_matrix.append(row)
        return Matrix(tensor_matrix)

    @staticmethod
    def identity_matrix(n):
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(img(1, 0))
                else:
                    row.append(img(0, 0))
            matrix.append(row)
        return Matrix(matrix)

    def Frobenius_norm(self):
        total = img(0, 0)
        for i in range(self.no_of_rows):
            for j in range(self.no_of_columns):
                val = self.matrix[i][j]
                if not isinstance(val, img):
                    val = img(val, 0)
                total += val * val.conjugate()
        return total.mod()

    def __str__(self):
        return "\n".join([" ".join(str(x) for x in row) for row in self.matrix])
   
    def __repr__(self):
        return "Matrix.matrix(m,n)"
   
    @staticmethod
    def help():
        """Comprehensive help documentation for Matrix class with complex number support"""
        help_text = """
    =============================================== Matrix Class Help ===============================================
    Complete documentation for quantum computing matrix operations with complex 'img' support


    CONSTRUCTOR:
        Matrix([[1,2],[3,4]])                    -> Create matrix from nested lists
        Matrix.matrix(m, n)                      -> Interactive matrix input
        Matrix.random(m, n, (a,b))               -> Random integer matrix [a,b]
        Matrix.identity_matrix(n)                -> n×n identity matrix with img(1,0)


    BASIC OPERATIONS:
        m1 + m2                                  -> Matrix addition (same dimensions)
        m1 - m2                                  -> Matrix subtraction  
        m1 * m2                                  -> Matrix multiplication (m×n × n×p)
        scalar * m1                              -> Scalar multiplication (int/float/img)
        m1 ^ m2                                  -> Element-wise (Hadamard) product
        m1 == m2                                 -> Exact equality check
        m1^n                                     -> Matrix power (integer n only)


    EDITING:
        m.edit_element(row, col, value)          -> Change single element (1-indexed)
        m.edit_row(row, new_row)                 -> Replace entire row (1-indexed)
        m.edit_column(col, new_col)              -> Replace entire column (1-indexed)


    INDEXING: (NEW!)
        m[0,0]                                   -> Get element at row 0, col 0 (0-indexed)
        m.value()                                -> Get single value from 1×1 matrix


    DISPLAY:
        m.show("Label")                          -> Pretty print with label
        print(m)                                 -> Basic string representation
        m.order()                                -> [m, n] list m->rows,n->columns


    PROPERTIES & NORMS:
        m.trace()                                -> Sum of diagonal elements (complex)
        m.det()                                  -> Determinant (recursive, complex)
        m.Frobenius_norm()                       -> √(Σ|elements|²) magnitude
        m.max_size_element()                     -> Max character width for printing




    TRANSFORMATIONS:
        m.transpose("new"/"modify")              -> Transpose matrix
        m.conjugate_transpose()                  -> Hermitian adjoint (U†)
        m.adjoint()                              -> Classical adjoint (cofactors)
        m.inverse()                              -> Matrix inverse (det ≠ 0)




    QUANTUM CHECKS:
        m.unitary_check()                        -> Checks if U†U = I (quantum gates)
        m.orthogonal_check(tol=1e-9)             -> Checks if UUT = I (real orthogonal)
        Matrix.is_identity(m, tol=1e-9)          -> Checks if matrix ≈ identity


    TENSOR & SPECIAL:
        m.tensor(other)                          -> Kronecker tensor product
        Matrix.rearrange(m)                      -> Row echelon form prep


    EXAMPLES:
        # Pauli-X gate (NOT gate)
        X = Matrix([[0,img(1,0)],[img(1,0),0]])
        print(X.unitary_check())  # True
       
        # Hadamard gate
        H = (img(1/math.sqrt(2),0)) * Matrix([[1,1],[1,-1]])
        print(H.unitary_check())  # True


    COMPLEX NUMBER SUPPORT:
        All operations fully support 'img' complex numbers
        img(a,b) = a + bi
        Uses .mod() for magnitude, .conjugate() for *, .real/.imag properties


    ERROR HANDLING:
        Returns descriptive messages for invalid operations
        Raises ValueError for singular matrices, non-square operations
        Tolerance-based floating point comparisons (tol=1e-9)


    PERFORMANCE NOTES:
        Pure Python implementation - educational/quantum simulation focused
        Recursive determinant (n≤10 recommended)
        No external dependencies except 'img' class

        """
        print(help_text)


if __name__ == "__main__":
    Matrix.help()