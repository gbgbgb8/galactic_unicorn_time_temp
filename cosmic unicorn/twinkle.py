import random
from colors import colors  # Import the colors dictionary from colors.py

class Twinkle:
    def __init__(self, width, height, num_pixels=5):
        self.width = width
        self.height = height
        self.num_pixels = num_pixels
        self.pixels = [(random.randint(0, width - 1), random.randint(0, height - 1)) for _ in range(num_pixels)]
        self.colors = [random.choice(list(colors.keys())) for _ in range(num_pixels)]
        self.steps = [random.randint(0, 10) for _ in range(num_pixels)]

    def update(self, graphics):
        for i in range(self.num_pixels):
            x, y = self.pixels[i]
            color = self.colors[i]
            step = self.steps[i]

            # Calculate the brightness based on the current step
            brightness = abs(step - 5) / 5

            # Set the color with the calculated brightness
            graphics.set_pen(graphics.create_pen(int(colors[color][0] * brightness),
                                                 int(colors[color][1] * brightness),
                                                 int(colors[color][2] * brightness)))
            graphics.pixel(x, y)

            # Update the step and reset if necessary
            self.steps[i] = (step + 1) % 20
            if self.steps[i] == 0:
                self.pixels[i] = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
                self.colors[i] = random.choice(list(colors.keys()))

