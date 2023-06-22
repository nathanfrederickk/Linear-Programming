class LinearProgramming:
    def __init__(self, filename) -> None:
        """
        To compute linear inequalties equations and provide the most
        optimal answer based on the constraints given from the input file.
        """

        # the number of decision variables
        self.num_of_decision_variables = 0
        # the coefficients of the decision variables
        self.objective_list = []

        # the number of constraints
        self.num_of_constraints = 0

        # the coefficients of the variables in the LHS of the equation
        self.constraints_lhs_matrix = []

        # the value in the RHS of the equation
        self.constraints_rhs_vector = []

        # starts reading the input file
        self.read_file(filename)
        
        # the coefficients of the non-fixed variables
        self.coefficients_row = [0] * self.num_of_constraints

        # the coefficients of the fixed and non_fixed variables
        self.coefficients_column = [0] * (self.num_of_constraints + self.num_of_decision_variables)
        self.initialize_coefficients()

        # the matrix used
        self.matrix  = []
        self.initialize_matrix()

        # the zj values
        self.zj = [0] * (self.num_of_constraints + self.num_of_decision_variables + 1)

        # the zj-cj values
        self.cj_zj = [0] * (self.num_of_constraints + self.num_of_decision_variables)
        self.count_cj_zj()

        # tethta values
        self.tetha = [0] * (self.num_of_constraints)

        # storing the answers
        self.var_ans_index = []

        # the index of the entering variable
        for i in range(self.num_of_decision_variables):
            self.var_ans_index.append([i, -1])

        # run the algorithm
        self.run()

        # write the answer to a file
        self.print_result()
    
    def read_file(self, filename) -> None:
        """
        To read a file containing the linear programming problem with
        a format as in the assignment specification. The values read will
        be stored in the instance variables.
        """
        text = ""

        file = open(filename)

        checkpoint = ""

        for line in file:

            if text == '# numDecisionVariables':
                self.num_of_decision_variables = int(line.strip())
            
            elif text == '# numConstraints':
                self.num_of_constraints = int(line.strip())
            
            elif text == '#objective' or text == '# objective':
                self.objective_list = [int(num) for num in line.strip().split(', ')]
            
            elif text == '# constraintsLHSMatrix' or checkpoint == 'constraintsLHSMatrix' and line.strip() != '# constraintsRHSVector':
                    self.constraints_lhs_matrix += [[int(num) for num in line.strip().split(', ')]]
            
            elif text == '# constraintsRHSVector' or checkpoint == 'constraintsRHSVector':
                    self.constraints_rhs_vector.append(int([num for num in line.strip().split(' ')][0]))


            text = line.strip()

            if text == '# constraintsLHSMatrix':
                checkpoint = 'constraintsLHSMatrix'

            elif text == '# constraintsRHSVector':
                checkpoint = 'constraintsRHSVector'


        file.close()

    def initialize_coefficients(self):
        """
        To initialize the coefficients of the fixed and non-fixed variables
        """
        for i in range(self.num_of_decision_variables):
            self.coefficients_column[i] = self.objective_list[i]

    def new_matrix(self):
        """
        To create a new matrix with the size of the number of constraints as the 
        number of rows and the number of decision variables + number of constraints
        as the column. All the items inside the matrix will be initialized to 0.
        """
        total_values = self.num_of_constraints + self.num_of_decision_variables
        matrix = [None] * self.num_of_constraints

        for i in range(len(matrix)):
            matrix[i] = [0] * total_values

        return matrix
    
    def initialize_matrix_values(self):
        """
        To initialize the values of the matrix with the values from the constraints and
        the deceision variables.
        """
        counter = self.num_of_decision_variables

        for i in range(len(self.matrix)):
            for y in range(len(self.constraints_lhs_matrix[i])):
                self.matrix[i][y] = self.constraints_lhs_matrix[i][y]
            
            self.matrix[i][counter] = 1
            counter += 1
        return
    
    def initialize_matrix(self):
        """
        Initialize the matrix with the values from the constraints and the decision variables.
        """
        self.matrix = self.new_matrix()
        self.initialize_matrix_values()

        return 
    
    def count_zj(self):
        """
        To count the zj values for each column in the matrix.
        """

        def count_zj_aux(column_index: int) -> int:
            """
            To count the zj value for the columns in the fixed and non-fixed variables.
            """
            total = 0

            # loop through the rows
            for y in range(len(self.matrix)):
                total += self.matrix[y][column_index] * self.coefficients_row[y]
            
            return total
        
        def count_zj_rhs() -> int:
            """
            To count the zj value for the columns in RHS value of the constraints.
            """
            total = 0
            
            # loop through the rows of the RHS values
            for y in range(len(self.constraints_rhs_vector)):
                total += self.coefficients_row[y] * self.constraints_rhs_vector[y]

            return total

        for i in range(len(self.zj) - 1):
            self.zj[i] = count_zj_aux(i)
        
        self.zj[-1] = count_zj_rhs()
        
        return
    
    def count_cj_zj(self):
        """
        To count the cj-zj values for each column in the matrix not including
        the RHS column.
        """
        for i in range(len(self.cj_zj)):
            self.cj_zj[i] = self.coefficients_column[i] - self.zj[i]

        return
    
    def find_biggest(self, target_list: list) -> tuple:
        """ 
        Find the biggest value in the target_list and returns
        the value and the index of the value.
        """
        big = target_list[0]
        index_return = 0

        # loops through the list
        for index in range(len(target_list)):

            # if the value is bigger than the current biggest value
            if target_list[index] > big:

                # set the new biggest value and the index of the value
                big = target_list[index]
                index_return = index

        return (big, index_return)
    
    def find_smallest_positive(self, target_list: list) -> tuple:
        """
        To find the smallest positive value in the target_list and returns
        the value and the index of the value.
        """
        small = target_list[0]
        index_return = 0

        # loops through the list
        for index in range(len(target_list)):

            # if the value is smaller than the current smallest value
            # and the value is positive
            if target_list[index] < small and target_list[index] >= 0 :

                # change the smallest value and the index of the value
                small = target_list[index]
                index_return = index

        return (small, index_return)
    
    def modify_tetha(self, index_column: int):
        """
        To modify the tetha values in the tetha list. This is done
        by dividing the RHS value of the constraints with the value
        in the index_column of the matrix.
        """
        for i in range(len(self.tetha)):
            
            # if the value in the index_column is not 0
            try:
                self.tetha[i] = self.constraints_rhs_vector[i] / self.matrix[i][index_column]
            
            # if the value in the index_column is 0, it will be set to -1
            # this is so that the value will not be chosen as the smallest positive value
            except:
                self.tetha[i] = -1
    
    def run(self):
        """
        To solve the actual linear programming problem.

        :Complexity:
        :Time           : O(N^M), where N is the number of variables and M is the number of constraints
        """

        # find the biggest value in the cj-zj list
        maximum, index_max = self.find_biggest(self.cj_zj)

        # while the maximum is bigger than 0
        while maximum > 0:

            # modify the tetha values using the function
            self.modify_tetha(index_max)

            # find the smallest positive value in the tetha list
            minimum, index_min = self.find_smallest_positive(self.tetha)

            # if the index_max is smaller than the number of decision variables,
            # then it is one of the decision variables, which will be included
            # in the final answer
            if index_max < self.num_of_decision_variables:

                # add the index_max to the list of the answer
                self.var_ans_index[index_max] = [index_max, index_min]

            # change the value of the coefficients_row of the index_min since
            # one of the non-fixed values will be replaced
            self.coefficients_row[index_min] = self.coefficients_column[index_max]

            # find the intersection value
            intersection = self.matrix[index_min][index_max]

            # divide the row of the index_min with the intersection value
            for i in range(len(self.matrix[index_min])):
                self.matrix[index_min][i] /= intersection

            # divide the RHS value of the index_min with the intersection value
            self.constraints_rhs_vector[index_min] /= intersection

            # loop through the rows of the matrix
            for i in range(len(self.matrix)):
                # if i is the index_min, the row does not need to be modified
                if i == index_min:
                    continue
                
                # else, modify row i
                self.modify_matrix(i, index_max, index_min)

            # update the cj-zj and zj values
            self.count_zj()
            self.count_cj_zj()
            
            # update the maximum value of the cj-zj list
            maximum, index_max = self.find_biggest(self.cj_zj)



    def modify_matrix(self, index: int, index_max: int, index_min: int) -> int:
        """
        To modify the matrix and the RHS vector. This is needed if
        the maximum value is > 0.
        """
        # find the multiplier
        multiplier = (self.matrix[index][index_max]) / (self.matrix[index_min][index_max])

        # loop through the columns of the matrix
        for i in range(len(self.matrix[index])):
            # use the formula as described in the lecture videos
            self.matrix[index][i] -= (multiplier * self.matrix[index_min][i])

        # modify the RHS vector
        self.constraints_rhs_vector[index] -= (multiplier * self.constraints_rhs_vector[index_min])
        return 
    
    def round_modified(self, val: float) -> int:
        """
        To round the value to the nearest integer.
        """
        temp = val // 1
        decimal = val - temp

        if(decimal >= 0.5):
            return int(temp + 1)
        
        return int(temp)
    
    def print_result(self) -> None:
        """
        To print in the desireable format according to the assignment specification to 
        the lpsolution.txt file.

        Citation: Taken from my Assignment 1 FIT 3155
        """

        # to sort the list of the answer based on the decision variables
        self.var_ans_index = sorted(self.var_ans_index, key=lambda x: x[0])

        with open('lpsolution.txt', 'w') as f:  
            
            f.write('# optimalDecisions\n')

            for i in range(len(self.var_ans_index) - 1):

                index = self.var_ans_index[i][1]

                # if the index is -1, it means that the value is 0
                # since it is not used in the final answer
                if index == -1:
                    f.write(str(0) + ", ")
                    continue
                
                # round the value to the nearest integer before
                # writing it to the file
                f.write(str(self.constraints_rhs_vector[index]) + ", ")

            index = self.var_ans_index[-1][1]
            
            if index == -1:
                f.write(str(0) + "\n# optimalObjective\n")
            else:
                f.write(str(self.constraints_rhs_vector[index]) + "\n# optimalObjective\n")

            # optimal answer
            f.write(str(self.zj[-1]))

            f.close()      


if __name__ == '__main__':

    _, filename = sys.argv
    
    LinearProgramming(filename)
