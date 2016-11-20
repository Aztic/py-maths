import os
import re

class Function:
	def __init__(self, function=None):
		if function is None:
			function = '0'
		self.signs = ['+','-','*','/']
		self.functions = ['^','ln','sin','cos','tan','arcsin','arccos','arctan','sec','cosec','e']
		self.inverses = {'ln':'e', 'sin': 'arcsin','cos':'arccos','tan':'arctan','e':'ln'}
		self.derivates = {'+': 'Ap + Bp', '-':'Ap - Bp', '*': 'Ap * B + A * Bp', '/':'(Ap * B - A * Bp)/(B^2)',
						'ln':'1/(A)', 'sin':'cos(A)', 'cos':'-sin(A)','tan':'sec(A)^2', 'x':'1'}
		self.function = str(function)
		self.ext_f = self.external_f(function)
		self.der = self.derivate(function)

	def derivate(self,function):
		function = function.replace(' ','')
		if function == 'x':
			return '1'
		repls = ['A','B']
		repls_2 = ['Ap','Bp']
		clean = ['*1','+0']
		ext = self.external_f(function)
		der = ''
		if not ext:
			return '0'
		else:
			f = list(ext)[0]
			der = self.derivates[f]
			if f in self.signs:			
				for i, value in enumerate(repls):
					der = re.sub('\s{}\s'.format(value),ext[f][i],der)
				for i, value in enumerate(repls_2):
					if value in repls_2:
						der = re.sub('{}'.format(value),self.derivate(ext[f][i]),der)
				#if der == self.derivates[f]:
					#der = '0'
			else:
				der = re.sub('A',ext[f][0],self.derivates[f])
				temp = self.derivate(ext[f][0])
				if temp:
					der += ' * ' + temp
		der = der.replace(' ','')
		for i in clean:
			der = re.sub('\{}'.format(i),'',der)
		der = self._clean_zeroes(der)
		return der

	#Returns the external function or operator and the implicated elements as a dictionary
	#{'External_function': [(function)]} or {'Operator':[(left_side),(right_side)]}
	#A exception occurs with '^'. ['^':[(base),(exponent)]]

	def external_f(self,function):
		if not function or function.isdigit():
			return 0
		external = {}
		returned = {}
		opened = self._positions(function,'(')
		closed = self._positions(function,')')
		#Check if there is a parenthesis
		if opened and closed:
			returned = self._separate(opened,closed,len(function))
			for position in returned['allowed']:
				#Check signs
				for sign in self.signs:
					if sign in function[position[0]:position[1]+1].split():
						the_index = function.index(sign,position[0])
						external[sign] = [function[1:the_index-1], function[the_index+1:len(function)]]
						return external
			#Check functions
			for position in returned['allowed']:
				for f in self.functions:
					internal = function[position[0]:position[1]+1]
					#print(internal)
					if f == '^' and f in internal:
						the_index = function.index(f)
						place = self._previous(returned['intervals'],function,the_index)
						external[f] = [function[place[0]:place[1]+1] ,function[the_index+1]]
					elif f in internal:
						the_index = function.index(f)
						place = self._next(returned['intervals'],function,the_index)
						external[f] = [function[place[0]+1:place[1]]]
			return external
		else:
			for sign in self.signs:
				if sign in function:
					place = function.index(sign)
					external[sign] = [function[0:place], function[place+1:len(function)]]
					return external
			place = self._the_digit(function)
			if place:
				for i, value in enumerate(function):
					if not value.isdigit():
						external['*'] = [function[0:i],value]
						return external
					

		return None

	#Returns the previous function of a position
	def _previous(self,interval_f,function,position):
		if position == len(function)-1:
			return interval_f[-1]
		else:
			for i in range(len(interval_f)):
				if interval_f[i+1][0] > position:
					return interval_f[i]

	#Returns the next function of a position
	def _next(self,interval_f,function,position):
		if not position:
			return interval_f[0]
		else:
			for i in range(len(interval_f)):
				if interval_f[i][0] > position:
					return interval_f[i]

	#Returns a dictionary with the areas separates
	#'Allowed' = areas between functions (f1) this (f2)
	#'Intervals' = areas inside the parenthesis (this) + (this)

	def _separate(self,opened,closed,length):
		temp_list = []
		allowed_intervals = []
		returned = {}
		change = True
		while change:
			change = False
			if not temp_list:
				start = opened[0]
				end = closed[0]
			for i, value in enumerate(opened):
				if i == len(opened)-1:
					end = closed[-1]
					temp_list.append([start,end])
				elif value >= end:
					if value < closed[i]:
						end = closed[i]
					else:
						end = closed[i-1]
					temp_list.append([start,end])
					start = opened[i+1]
					end = closed[closed.index(end)+1]
					change = True
					break

		if temp_list[0][0]:
			start = 0
		else:
			start = temp_list[0][1] + 1
		if temp_list:
			for i, interval in enumerate(temp_list):
				if not start:
					allowed_intervals.append([start,interval[0]-1])
				else:
					if i != len(temp_list)-1:
						allowed_intervals.append([start,temp_list[i+1][0]])
					else:
						allowed_intervals.append([start,length])
				start = interval[1]+1
		returned['allowed'] = allowed_intervals
		returned['intervals'] = temp_list
		return returned


	#Returns a list with the index of all passed elements in a string
	#For example. All closed parenthesis in ln((8*3) + (2x+4))
	#[7,16,17]
	def _positions(self,string, item):
		temp_list = []
		while True:
			if not temp_list:
				a_max = 0
			else:
				a_max = max(temp_list) + 1

			try:
				temp_list.append(string.index(item,a_max,len(string)))
			except ValueError:
				break
		return temp_list

	def _the_digit(self,function):
		for i, value in enumerate(function):
			if value.isdigit():
				return [i,value]

	def _clean_zeroes(self,function):
		zeroes = ['*0','0*']
		limiters = self._positions(function,'+') + self._positions(function,'-')
		limiters.sort()
		for zero in zeroes:
			all_z = self._positions(function,zero)
			for pos in all_z:
				if pos < limiters[0]:
					function = function.replace(function[0:limiters[0]+1], '')
				else:
					for i, value in enumerate(limiters):
						if pos > limiters[i+1]:
							prev = value
							next_s = limiters[i+1]
							break
					function = function.replace(function[prev+1:next_s+1], '')	

		return function

