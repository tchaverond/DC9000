# -*- coding: utf-8 -*

from tkinter import*
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
import pickle
import copy

import Game



class Layout:

	def __init__(self):

		self.fenetre = Tk()
		self.fenetre.title("Deluxe Checkers 9000 (v1.0)")


		self.h = self.fenetre.winfo_screenheight() * 0.85
		self.w = min(self.fenetre.winfo_screenwidth() * 0.85, 1.5*self.h)


		# game engine : rules, pace...
		self.game = Game.Board()

		self.plz_h = min(self.h,0.67*self.w)		# board height
		self.plz_w = self.plz_h						# board width


		# grid design
		self.design = "old"


		# graphical parameters
		# self.cs = 59 				# square size (height and width)
		# self.x_gap = 6 			# x gap between 2 squares
		# self.y_gap = 6 			# y gap between 2 squares
		# self.size = 54 			# piece size
		self.cs = (0.1*self.plz_h)-1				# square size (height and width)
		self.x_gap = 0.1*self.cs 				# x gap between 2 squares
		self.y_gap = 0.1*self.cs				# y gap between 2 squares
		self.size = self.cs - self.x_gap 				# piece size


		# parameters for the cemetery (place where we draw the pieces that have been taken)
		# self.cemetery_cs = 18
		# self.cemetery_size = 12
		# self.cemetery_y_gap = 22
		self.cemetery_cs = 0.3*self.cs
		self.cemetery_size = self.cemetery_cs - self.x_gap
		self.cemetery_y_gap = 1.22*self.cemetery_cs



		# tkinter (graphical) objects
		world = PanedWindow(self.fenetre,height=self.h-1,width=self.w-1)
		self.playzone = Canvas(self.fenetre,height=self.plz_h-1,width=self.plz_w-1,bg='white')
		controls = PanedWindow(self.fenetre,height=self.plz_h-1,width=self.w-self.plz_w,orient=VERTICAL)

		self.playzone.create_rectangle(1,1,self.plz_h-2,self.plz_w-2)


		# label indicating the player whose turn it is
		self.player_now = StringVar()
		self.player_now.set("Now playing : Green")
		label_player = Label(controls,textvariable=self.player_now,height=4)

		controls.add(label_player)


		# canvas to draw the pieces taken by opponent
		self.cemetery = Canvas(controls,height=100)

		controls.add(self.cemetery)


		# auto-rotation checkbox
		self.autorot = IntVar()
		self.autorot.set(0)
		check_autorot = Checkbutton(controls,text="Auto-rotate",variable=self.autorot,height=15)

		controls.add(check_autorot)


		# cancel button
		cancel_button = Button(controls,text="Cancel",command=self.cancel)

		controls.add(cancel_button)



		# menu
		menubar = Menu(self.fenetre)

		gamemenu = Menu(menubar, tearoff=0)
		gamemenu.add_command(label="Reset",command=self.reset)
		gamemenu.add_command(label="Import",command=self.import_cfg)
		gamemenu.add_command(label="Export",command=self.export_cfg)
		gamemenu.add_command(label="Quit",command=self.quit)
		menubar.add_cascade(label="Game",menu=gamemenu)

		designmenu = Menu(menubar, tearoff=0)
		designmenu.add_command(label="SCCD9",command=self.old_design)
		designmenu.add_command(label="Wood",command=self.wood_design)
		menubar.add_cascade(label="Design",menu=designmenu)

		self.fenetre.config(menu=menubar)



		world.add(self.playzone)
		world.add(controls)
		world.pack()



		# import/export options
		self.file_options = {}
		self.file_options['defaultextension'] = '.dc9'
		self.file_options['initialdir'] = '.\DC9000\Configs'
		self.file_options['filetypes'] = [('DC9000 files', '.dc9'), ('all files', '.*')]
		self.file_options['parent'] = self.fenetre


		# event listener for left clicks on board
		self.playzone.bind("<Button-1>", self.left_click)


		# drawing the board for the first time
		self.draw_grid_2(self.game.grid)



	def import_cfg (self) :

		self.file_options['initialfile'] = ""
		filename = filedialog.askopenfilename(**self.file_options)

		if filename :
			fin = open(filename,"rb")
			cfg = pickle.load(fin)
			self.game.init_custom(cfg)
			fin.close()
			self.refresh()

		else :
			messagebox.showerror("Deluxe Checkers 9000","No input file provided.")


	def export_cfg (self) :

		self.file_options['initialfile'] = "config1"
		filename = filedialog.asksaveasfilename(**self.file_options)

		if filename :
			fout = open(filename,"wb")
			pickle.dump([self.game.grid,self.game.queens,self.game.player,self.game.cur_turn],fout)
			fout.close()

		else :
			messagebox.showerror("Deluxe Checkers 9000","No file name provided.")



	def old_design (self) :
		self.design = "old"
		self.refresh()

	def wood_design (self) :
		self.design = "wood"
		self.refresh()



	# drawing the grid with player 1 below
	def draw_grid_1 (self, grid, queens = []) :

		self.playzone.delete("all")

		if self.design == "old" :

			for i in range(len(grid)) :
				for j in range(len(grid)) :
					if grid[i][j] != -1 :
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap),self.plz_h-(self.cs*j+self.y_gap),self.plz_w-(self.cs*i+self.x_gap+self.size),self.plz_h-(self.cs*j+self.y_gap+self.size),outline='black')
					
					if grid[i][j] == 1 :
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap+self.size/4),self.plz_h-(self.cs*j+self.y_gap+self.size/4),self.plz_w-(self.cs*i+self.x_gap+3*self.size/4),self.plz_h-(self.cs*j+self.y_gap+3*self.size/4),outline='#d00',fill='#d00')
						if [i,j] in queens :
							self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap+self.size/16),self.plz_h-(self.cs*j+self.y_gap+self.size/16),self.plz_w-(self.cs*i+self.x_gap+15*self.size/16),self.plz_h-(self.cs*j+self.y_gap+15*self.size/16),outline='#d00',fill='#d00')

					if grid[i][j] == 2 :
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap+self.size/4),self.plz_h-(self.cs*j+self.y_gap+self.size/4),self.plz_w-(self.cs*i+self.x_gap+3*self.size/4),self.plz_h-(self.cs*j+self.y_gap+3*self.size/4),outline='#080',fill='#080')
						if [i,j] in queens :
							self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap+self.size/16),self.plz_h-(self.cs*j+self.y_gap+self.size/16),self.plz_w-(self.cs*i+self.x_gap+15*self.size/16),self.plz_h-(self.cs*j+self.y_gap+15*self.size/16),outline='#080',fill='#080')

		elif self.design == "wood" :

			for i in range(len(grid)) :
				for j in range(len(grid)) :
					if grid[i][j] == -1 :
						self.playzone.create_rectangle(self.plz_w-self.cs*i,self.plz_h-self.cs*j,self.plz_w-self.cs*(i+1),self.plz_h-self.cs*(j+1),fill='#fa3',outline='#000')
					else :
						self.playzone.create_rectangle(self.plz_w-self.cs*i,self.plz_h-self.cs*j,self.plz_w-self.cs*(i+1),self.plz_h-self.cs*(j+1),fill='#850',outline='#000')
					
					if grid[i][j] == 1 :
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap/2+self.size/8),self.plz_h-(self.cs*j+self.y_gap/2+self.size/6),self.plz_w-(self.cs*i+self.x_gap/2+5*self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+3*self.size/4),outline='#000',fill='#210')
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap/2+self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+self.size/4),self.plz_w-(self.cs*i+self.x_gap/2+5*self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+3*self.size/4),outline='#000',fill='#320')
						if [i,j] in queens :
							self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap/2+self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+self.size/4),self.plz_w-(self.cs*i+self.x_gap/2+5*self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+3*self.size/4),outline='#000',fill='#320')

					if grid[i][j] == 2 :
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap/2+self.size/8),self.plz_h-(self.cs*j+self.y_gap/2+self.size/6),self.plz_w-(self.cs*i+self.x_gap/2+5*self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+3*self.size/4),outline='#000',fill='#ed8')
						self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap/2+self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+self.size/4),self.plz_w-(self.cs*i+self.x_gap/2+5*self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+3*self.size/4),outline='#000',fill='#fe9')
						if [i,j] in queens :
							self.playzone.create_oval(self.plz_w-(self.cs*i+self.x_gap/2+self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+self.size/4),self.plz_w-(self.cs*i+self.x_gap/2+5*self.size/6),self.plz_h-(self.cs*j+self.y_gap/2+3*self.size/4),outline='#000',fill='#fe9')


	# drawing the grid with player 2 below
	def draw_grid_2 (self, grid, queens = []) :

		self.playzone.delete("all")

		if self.design == "old" :
		
			for i in range(len(grid)) :
				for j in range(len(grid)) :
					if grid[i][j] != -1 :
						self.playzone.create_oval(self.cs*i+self.x_gap,self.cs*j+self.y_gap,self.cs*i+self.x_gap+self.size,self.cs*j+self.y_gap+self.size,outline='black')
					
					if grid[i][j] == 1 :
						self.playzone.create_oval(self.cs*i+self.x_gap+self.size/4,self.cs*j+self.y_gap+self.size/4,self.cs*i+self.x_gap+3*self.size/4,self.cs*j+self.y_gap+3*self.size/4,outline='#d00',fill='#d00')
						if [i,j] in queens :
							self.playzone.create_oval(self.cs*i+self.x_gap+self.size/16,self.cs*j+self.y_gap+self.size/16,self.cs*i+self.x_gap+15*self.size/16,self.cs*j+self.y_gap+15*self.size/16,outline='#d00',fill='#d00')

					if grid[i][j] == 2 :
						self.playzone.create_oval(self.cs*i+self.x_gap+self.size/4,self.cs*j+self.y_gap+self.size/4,self.cs*i+self.x_gap+3*self.size/4,self.cs*j+self.y_gap+3*self.size/4,outline='#080',fill='#080')
						if [i,j] in queens :
							self.playzone.create_oval(self.cs*i+self.x_gap+self.size/16,self.cs*j+self.y_gap+self.size/16,self.cs*i+self.x_gap+15*self.size/16,self.cs*j+self.y_gap+15*self.size/16,outline='#080',fill='#080')

		elif self.design == "wood" :

			for i in range(len(grid)) :
				for j in range(len(grid)) :
					if grid[i][j] == -1 :
						self.playzone.create_rectangle(self.cs*i,self.cs*j,self.cs*(i+1),self.cs*(j+1),fill='#fa3',outline='#000')
					else :
						self.playzone.create_rectangle(self.cs*i,self.cs*j,self.cs*(i+1),self.cs*(j+1),fill='#850',outline='#000')
					
					if grid[i][j] == 1 :
						self.playzone.create_oval(self.cs*i+self.x_gap/2+self.size/6,self.cs*j+self.y_gap/2+self.size/4,self.cs*i+self.x_gap/2+7*self.size/8,self.cs*j+self.y_gap/2+5*self.size/6,outline='#000',fill='#210')
						self.playzone.create_oval(self.cs*i+self.x_gap/2+self.size/6,self.cs*j+self.y_gap/2+self.size/4,self.cs*i+self.x_gap/2+5*self.size/6,self.cs*j+self.y_gap/2+3*self.size/4,outline='#000',fill='#320')
						if [i,j] in queens :
							self.playzone.create_oval(self.cs*i+self.x_gap+self.size/16,self.cs*j+self.y_gap+self.size/16,self.cs*i+self.x_gap+15*self.size/16,self.cs*j+self.y_gap+15*self.size/16,outline='#000',fill='#320')

					if grid[i][j] == 2 :
						self.playzone.create_oval(self.cs*i+self.x_gap/2+self.size/6,self.cs*j+self.y_gap/2+self.size/4,self.cs*i+self.x_gap/2+7*self.size/8,self.cs*j+self.y_gap/2+5*self.size/6,outline='#000',fill='#ed8')
						self.playzone.create_oval(self.cs*i+self.x_gap/2+self.size/6,self.cs*j+self.y_gap/2+self.size/4,self.cs*i+self.x_gap/2+5*self.size/6,self.cs*j+self.y_gap/2+3*self.size/4,outline='#000',fill='#fe9')
						if [i,j] in queens :
							self.playzone.create_oval(self.cs*i+self.x_gap+self.size/16,self.cs*j+self.y_gap+self.size/16,self.cs*i+self.x_gap+15*self.size/16,self.cs*j+self.y_gap+15*self.size/16,outline='#000',fill='#fe9')


	# drawing the cemetery (containing all pieces taken by the opponent)
	def draw_cemetery (self, grid, queens = []) :

		self.cemetery.delete("all")
		# number of pieces taken = 20 - pieces left - queens (as a queen worths 2 pieces)
		red_taken = 20 - sum([i.count(1) for i in grid]) - len([1 for i in queens if grid[i[0]][i[1]] == 1])
		green_taken = 20 - sum([i.count(2) for i in grid]) - len([1 for i in queens if grid[i[0]][i[1]] == 2])
		
		# drawing on 2 lines, for easier understanding
		if self.design == "old" :
			for i in range(red_taken) :
				if i < 10 :
					self.cemetery.create_oval(self.cemetery_cs*i+self.x_gap,self.y_gap,self.cemetery_cs*i+self.x_gap+self.cemetery_size,self.y_gap+self.cemetery_size,outline='#d00',fill='#d00')
				else :
					self.cemetery.create_oval(self.cemetery_cs*(i-10)+self.x_gap,self.cemetery_y_gap+self.y_gap,self.cemetery_cs*(i-10)+self.x_gap+self.cemetery_size,self.y_gap+self.cemetery_y_gap+self.cemetery_size,outline='#d00',fill='#d00')

		elif self.design == "wood" :
			for i in range(red_taken) :
				if i < 10 :
					self.cemetery.create_oval(self.cemetery_cs*i+self.x_gap,self.y_gap,self.cemetery_cs*i+self.x_gap+self.cemetery_size,self.y_gap+self.cemetery_size,outline='#000',fill='#320')
				else :
					self.cemetery.create_oval(self.cemetery_cs*(i-10)+self.x_gap,self.cemetery_y_gap+self.y_gap,self.cemetery_cs*(i-10)+self.x_gap+self.cemetery_size,self.y_gap+self.cemetery_y_gap+self.cemetery_size,outline='#000',fill='#320')


		if self.design == "old" :
			for i in range(green_taken) :
				if i < 10 :
					self.cemetery.create_oval(self.cemetery_cs*i+self.x_gap,self.y_gap+2*self.cemetery_y_gap,self.cemetery_cs*i+self.x_gap+self.cemetery_size,self.y_gap+2*self.cemetery_y_gap+self.cemetery_size,outline='#080',fill='#080')
				else :
					self.cemetery.create_oval(self.cemetery_cs*(i-10)+self.x_gap,self.y_gap+3*self.cemetery_y_gap,self.cemetery_cs*(i-10)+self.x_gap+self.cemetery_size,self.y_gap+3*self.cemetery_y_gap+self.cemetery_size,outline='#080',fill='#080')

		elif self.design == "wood" :
			for i in range(green_taken) :
				if i < 10 :
					self.cemetery.create_oval(self.cemetery_cs*i+self.x_gap,self.y_gap+2*self.cemetery_y_gap,self.cemetery_cs*i+self.x_gap+self.cemetery_size,self.y_gap+2*self.cemetery_y_gap+self.cemetery_size,outline='#000',fill='#fe9')
				else :
					self.cemetery.create_oval(self.cemetery_cs*(i-10)+self.x_gap,self.y_gap+3*self.cemetery_y_gap,self.cemetery_cs*(i-10)+self.x_gap+self.cemetery_size,self.y_gap+3*self.cemetery_y_gap+self.cemetery_size,outline='#000',fill='#fe9')




	# method called by a left click on board
	def left_click (self, event) :

		# getting where the click has happened
		if self.autorot.get() == 1 :
			if self.game.player == 2 :
				x = int(event.x / (self.plz_h/len(self.game.grid)))
				y = int(event.y / (self.plz_w/len(self.game.grid)))

			else :
				x = int(10 - event.x/(self.plz_h/len(self.game.grid)))
				y = int(10 - event.y/(self.plz_w/len(self.game.grid)))
		else :
			x = int(event.x / (self.plz_h/len(self.game.grid)))
			y = int(event.y / (self.plz_w/len(self.game.grid)))



		# there are 2 possibilities : whether the player wants to select a piece or to move it

		if self.game.highlight == [] :					# if no piece is already selected (selecting a piece to move or huffing an opponent's one)
			self.game.select(x,y) 						# we call the "select" method in the game engine
														
		else :											# else the player wants to move a piece
			self.game.move(x,y)							# we call the "move" method

		self.refresh()



	def refresh (self) :

		# updating the drawing of the grid
		if self.autorot.get() == 1 :
			if self.game.player == 1 :
				self.draw_grid_1(self.game.grid,self.game.queens)
			else :
				self.draw_grid_2(self.game.grid,self.game.queens)
		else :
			self.draw_grid_2(self.game.grid,self.game.queens)

		self.draw_cemetery(self.game.grid,self.game.queens)


		# and highlighting the currently selected piece
		if self.game.highlight != [] :

			if self.autorot.get() == 1 :
				if self.game.player == 1 :
					self.highlight_piece_1(self.game.highlight)
				else :
					self.highlight_piece_2(self.game.highlight)
			else :
				self.highlight_piece_2(self.game.highlight)


		if self.game.player == 1 :
			if self.design == "old" :
				self.player_now.set("Now playing: Red")
			elif self.design == "wood" :
				self.player_now.set("Now playing: Black")
		else :
			if self.design == "old" :
				self.player_now.set("Now playing: Green")
			elif self.design == "wood" :
				self.player_now.set("Now playing: White")

		self.check_end()



	def highlight_piece_1 (self, coords) :

		if self.design == "old" :
			self.playzone.create_oval(self.plz_w-(self.cs*coords[0]+self.x_gap+self.size/6),self.plz_h-(self.cs*coords[1]+self.y_gap+self.size/6),self.plz_w-(self.cs*coords[0]+self.x_gap+5*self.size/6),self.plz_h-(self.cs*coords[1]+self.y_gap+5*self.size/6),outline='black')
		elif self.design == "wood" :
			self.playzone.create_oval(self.plz_w-(self.cs*coords[0]+self.x_gap/2+23*self.size/24),self.plz_h-(self.cs*coords[1]+self.y_gap/2+self.size/12),self.plz_w-(self.cs*coords[0]+self.x_gap/2+self.size/24),self.plz_h-(self.cs*coords[1]+self.y_gap/2+5*self.size/6),outline='black',dash=(2,2))



	def highlight_piece_2 (self, coords) :

		if self.design == "old" :
			self.playzone.create_oval(self.cs*coords[0]+self.x_gap+self.size/6,self.cs*coords[1]+self.y_gap+self.size/6,self.cs*coords[0]+self.x_gap+5*self.size/6,self.cs*coords[1]+self.y_gap+5*self.size/6,outline='black')
		elif self.design == "wood" :
			self.playzone.create_oval(self.cs*coords[0]+self.x_gap/2+self.size/24,self.cs*coords[1]+self.y_gap/2+self.size/6,self.cs*coords[0]+self.x_gap/2+23*self.size/24,self.cs*coords[1]+self.y_gap/2+11*self.size/12,outline='black',dash=(2,2))



	def check_end (self) :

		i = 0
		end = True
		while i < len(self.game.grid) and end == True :
			if 1 in self.game.grid[i] :
				end = False
			i = i+1

		if end == True :
			if self.design == "old" :
				self.player_now.set("Green player victory!")
			elif self.design == "wood" :
				self.player_now.set("White player victory!")

		i = 0
		end = True
		while i < len(self.game.grid) and end == True :
			if 2 in self.game.grid[i] :
				end = False
			i = i+1

		if end == True :
			if self.design == "old" :
				self.player_now.set("Red player victory!")
			elif self.design == "wood" :
				self.player_now.set("Black player victory!")



	def reset (self) :

		self.fenetre.destroy()
		os.system("python Interface.py")


	def quit (self) :

		self.fenetre.destroy()


	# cancels the last move done on board
	def cancel (self) :

		if self.game.history[1] != None :

			self.game.cancel()
			self.refresh()


	# (tkinter's mainloop)
	def loop (self) :

		self.fenetre.mainloop()




Checkers = Layout()
Checkers.loop()