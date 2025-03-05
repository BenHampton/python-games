from utils.utility import Utility

class Button:
	def __init__(self, image, pos, text_input):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = Utility.get_font('doom.ttf', 75)
		self.base_color = 'white'
		self.hovering_color = (252, 2, 3)
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text

		# todo Rect( (left, top), (width, height))
		self.rect = self.image.get_rect(bottomleft=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(bottomleft=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect,
					((self.text.get_width() // 2) - (self.image.get_width() // 2),
					 -10,
					 self.image.get_width(),
					 self.image.get_height()))

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)