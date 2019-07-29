import random
from time import time
from copy import deepcopy

class Team73:

	def __init__(self):
		self.position_weights = ((4,2,4),(2,3,2),(4,2,4)) 
		self.random_store = [[[[long(0) for l in xrange(2)] for j in xrange(9)] for i in xrange(9)] for k in xrange(2)]
		self.max_points = 100
		self.starttime = 0
		self.total_time = 22.5
		self.hard_total_time = 23.1
		self.hard_timeout = 0
		self.soft_timeout = 0
		self.store_board_heuristic = {} 
		self.store_block_heuristic = {}

		store_patterns = []
		store_diagonal = []

		store_diagonal_array1 = []
		store_diagonal_array2 = []
		for i in xrange(3):
			row_array = [] 
			col_array = [] 
			for j in xrange(3):
				row_array.append((i,j))
				col_array.append((j,i))
			store_patterns.append(tuple(row_array))
			store_patterns.append(tuple(col_array))
			store_diagonal_array1.append((i,i))
			store_diagonal_array2.append((i,2-i))
		store_patterns.append(store_diagonal_array1)
		store_patterns.append(store_diagonal_array2)
		store_diagonal.append(store_diagonal_array1)
		store_diagonal.append(store_diagonal_array2)

		self.store_patterns = tuple(store_patterns)[::-1]
		self.store_diagonal = tuple(store_diagonal)

		self.board_hash = long(0)
		self.block_hash = [[[long(0) for j in xrange(3)] for i in xrange(3)] for k in xrange(2)]
		self.hash_init()

	def hash_init(self):
			for i in xrange(2):
				for j in xrange(9):
					for k in xrange(9):
						for l in xrange(2):
							self.random_store[i][j][k][l] = long(random.randint(1, 2**64))

	def hash_move(self, cell, player):
		self.board_hash ^=  self.random_store[cell[0]][cell[1]][cell[2]][player]
		self.block_hash[cell[0]][cell[1]/3][cell[2]/3] ^=  self.random_store[cell[0]][cell[1]][cell[2]][player]

	def opponent_player(self, player):
		return 'o' if player == 'x' else 'x'

	def board_heuristic(self, block_heuristic_arr):
		board_heuristic_value = 0
		for k in xrange(2):
			for i in xrange(3):
				for j in xrange(3):
					if block_heuristic_arr[k][i][j] > 0:
						board_heuristic_value += 0.02 * self.position_weights[i][j] * block_heuristic_arr[k][i][j]
		return board_heuristic_value


	def board_pattern_checker(self, pattern_position, block_heuristic_arr):
		player_count = 0
		pattern_heuristic = 0
		multiplier = 1

		for k in xrange(2):
			for pos in pattern_position:
				val = block_heuristic_arr[k][pos[0]][pos[1]]
				pattern_heuristic += val
				if val == self.max_points:
					player_count += 1
				elif val < 0:
					return 0

			if player_count == 2:
				multiplier += 150
			elif player_count == 3:
				multiplier += 100000

		return multiplier * pattern_heuristic

	def board_diagonal_checker(self, pattern_position, block_heuristic_arr):
		player_count = 0
		pattern_heuristic = 0
		multiplier = 1

		for k in xrange(2):
			for pos in pattern_position:
				val = block_heuristic_arr[k][pos[0]][pos[1]]
				pattern_heuristic += val
				if val == self.max_points:
					player_count += 1
				elif val < 0:
					return 0

			if player_count == 2:
				multiplier += 50

		return multiplier * pattern_heuristic

	def diagonal_checker(self, flag, block, pattern_position) :
		player_count = 0

		for pos in pattern_position:
			if block[pos[0]][pos[1]] == self.opponent_player(flag):
				return 0
			elif block[pos[0]][pos[1]] == flag:
				player_count += 1
		if player_count == 2:
			return 2
		return 0

	def pattern_checker(self, flag, block, pattern_positionay):
		player_count = 0

		for pos in pattern_positionay:
			if block[pos[0]][pos[1]] == self.opponent_player(flag):
				return 0
			elif block[pos[0]][pos[1]] == flag:
				player_count += 1

		if player_count == 2:
			return 4
		elif player_count == 3:
			return 100
		return 0

	def block_heuristic(self,flag,block):
		block_heuristic_value = 0

		for dg_arr in self.store_diagonal:
			val = self.diagonal_checker(flag,block,dg_arr)
			block_heuristic_value += val
		for pattern_position in self.store_patterns:
			val = self.pattern_checker(flag,block,pattern_position)
			block_heuristic_value += val

		for i in xrange(3):
			for j in xrange(3):
				if block[i][j] == flag:
					block_heuristic_value += 0.1 * self.position_weights[i][j]

		return block_heuristic_value


	def heuristic(self,flag,board):
		if (self.board_hash, flag) in self.store_board_heuristic:
			return self.store_board_heuristic[(self.board_hash, flag)]
		
		blocks = board.small_boards_status
		b = board.big_boards_status
		
		block_heuristic_arr = [[[0 for j in xrange(3)] for i in xrange(3)] for k in xrange(2)]

		for k in xrange(2):
			for i in xrange(3):
				for j in xrange(3):
					if self.soft_timeout or self.hard_timeout:
						return -1000000000
					if blocks[k][i][j]==flag:
						block_heuristic_arr[k][i][j] = self.max_points
					elif blocks[k][i][j]==self.opponent_player(flag) or blocks[k][i][j]=='d':
						block_heuristic_arr[k][i][j] = -1
					else:
						block = tuple([tuple(b[k][3*i + x][3*j:3*(j+1)]) for x in xrange(3)])
						if (self.block_hash[k][i][j],flag) in self.store_block_heuristic:
							block_heuristic_arr[k][i][j] = self.store_block_heuristic[(self.block_hash[k][i][j],flag)]
						else:
							block_heuristic_arr[k][i][j] = self.block_heuristic(flag,block)
							self.store_block_heuristic[(self.block_hash[k][i][j],flag)] = block_heuristic_arr[k][i][j]

		total = 0

		for dg_arr in self.store_diagonal:
			val = self.board_diagonal_checker(dg_arr,block_heuristic_arr)
			total += val
		for pattern_position in self.store_patterns:
			val = self.board_pattern_checker(pattern_position,block_heuristic_arr)
			total += val

		val = self.board_heuristic(block_heuristic_arr)
		total += val

		self.store_board_heuristic[(self.board_hash,flag)] = total
		return total

	
	
	def minimax(self, board, flag, depth, max_depth, alpha, beta, old_move, prev_move_bonus):

		if self.hard_timeout == 1 :
			return 0 , "temp"

		if time() - self.starttime >= self.hard_total_time :
			self.hard_timeout = 1
			return 0 , "temp"

		is_goal = board.find_terminal_state()

		if is_goal[1] == 'DRAW':
			return -100000, "temp"
		elif is_goal[1] == 'WON':
			if is_goal[0] == self.mysign:
				return float('inf'), "temp"
			else:
				return float('-inf'), "temp"


		if self.soft_timeout == 1 :
			return 0 , "temp"

		if time() - self.starttime >= self.total_time :
			self.soft_timeout = 1
			return 0 , "temp"

		if depth == max_depth:
			a = self.heuristic(self.mysign,board)
			b = self.heuristic(self.opponent_player(self.mysign),board)
			if a - 1.5*b >= 0:
				return ( a - b ) , "temp"
			else:
				return (a -1.5*b) , "temp"

		valid_cells = board.find_valid_move_cells(old_move)
		# random.shuffle(valid_cells)

		if flag==self.mysign:

			maxima_val = float('-inf')
			max_index = 0
			for i in xrange(len(valid_cells)):

				cell = valid_cells[i]
				suc, x = self.update(board, old_move,cell,flag)
				self.hash_move(cell,1)

				if x == True and prev_move_bonus == 0:
					val = self.minimax(board,flag,depth+1,max_depth,alpha,beta,cell,1)[0]
				else:
					val = self.minimax(board,self.opponent_player(flag),depth+1,max_depth,alpha,beta,cell,0)[0]

				if val > maxima_val:
					maxima_val = val
					max_index = i
				if maxima_val > alpha:
					alpha = maxima_val

				board.big_boards_status[cell[0]][cell[1]][cell[2]] = '-'
				board.small_boards_status[cell[0]][cell[1]/3][cell[2]/3] = '-'
				self.hash_move(cell,1)

				if beta <= alpha or self.soft_timeout or self.hard_timeout:
					break
			return maxima_val, valid_cells[max_index]

		else:
			minima_val = float('inf')
			for i in xrange(len(valid_cells)):

				cell = valid_cells[i]
				suc, x = self.update(board, old_move,cell,flag)
				self.hash_move(cell,0)

				if x == True and prev_move_bonus == 0:
					val = self.minimax(board,flag,depth+1,max_depth,alpha,beta,cell,1)[0]
				else:
					val = self.minimax(board,self.opponent_player(flag),depth+1,max_depth,alpha,beta,cell,0)[0]

				if val < minima_val:
					minima_val = val
				if minima_val < beta:
					beta = minima_val

				board.big_boards_status[cell[0]][cell[1]][cell[2]] = '-'
				board.small_boards_status[cell[0]][cell[1]/3][cell[2]/3] = '-'
				self.hash_move(cell,0)

				if beta <= alpha or self.soft_timeout or self.hard_timeout:
					break
			return minima_val, "temp"

	def update(self, board, old_move, new_move, ply):
		#updating the game board and small_board status as per the move that has been passed in the arguements
		board.big_boards_status[new_move[0]][new_move[1]][new_move[2]] = ply

		k = new_move[0]
		x = new_move[1]/3
		y = new_move[2]/3

		#checking if a small_board has been won or drawn or not after the current move
		bs = board.big_boards_status[k]
		for i in range(3):
			#checking for horizontal pattern(i'th row)
			if (bs[3*x+i][3*y] == bs[3*x+i][3*y+1] == bs[3*x+i][3*y+2]) and (bs[3*x+i][3*y] == ply):
				board.small_boards_status[k][x][y] = ply
				return 'SUCCESSFUL', True
			#checking for vertical pattern(i'th column)
			if (bs[3*x][3*y+i] == bs[3*x+1][3*y+i] == bs[3*x+2][3*y+i]) and (bs[3*x][3*y+i] == ply):
				board.small_boards_status[k][x][y] = ply
				return 'SUCCESSFUL', True
		#checking for store_diagonalonal store_patterns
		#store_diagonal 1
		if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == ply):
			board.small_boards_status[k][x][y] = ply
			return 'SUCCESSFUL', True
		#store_diagonal 2
		if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == ply):
			board.small_boards_status[k][x][y] = ply
			return 'SUCCESSFUL', True
		#checking if a small_board has any more cells left or has it been drawn
		for i in range(3):
			for j in range(3):
				if bs[3*x+i][3*y+j] =='-':
					return 'SUCCESSFUL', False
		board.small_boards_status[k][x][y] = 'd'
		return 'SUCCESSFUL', False

	def move(self, board, old_move, flag):

		self.starttime = time()
		self.soft_timeout = 0
		self.hard_timeout = 0

		if old_move == (-1,-1,-1):
			self.hash_move((0,2,2),1)
			return (0,2,2)
		elif board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.opponent_player(flag):
			self.hash_move(old_move,0)

		self.mysign = flag
		max_depth = 4
		valid_cells = board.find_valid_move_cells(old_move)
		best_move = valid_cells[0]
		while self.soft_timeout == 0 and self.hard_timeout == 0:
			self.board_hash_copy = self.board_hash

			self.block_hashSafeCopy = deepcopy(self.block_hash)
			copyboard = deepcopy(board)
			move = self.minimax(copyboard,flag,0,max_depth,float('-inf'),float('inf'),old_move,0)[1]
			if self.soft_timeout or self.hard_timeout:
				self.board_hash = self.board_hash_copy
				self.block_hash = deepcopy(self.block_hashSafeCopy)
				break
			best_move = move
			max_depth += 1
			del copyboard
		self.hash_move(best_move,1)
		
		return best_move