import random
import tkinter as tk

class GameObject(object):

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):

    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill='#3498db',
            outline='cyan',
        )
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            # Cek apakah objek yang ditumbuk adalah Brick (Asteroid) atau Paddle
            if isinstance(game_object, Brick):
                # Ambil koordinat pusat asteroid untuk pantulan yang lebih natural
                pass
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):

    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill='white',
            outline='gray',
        )
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    # Mengganti warna warni dengan tema abu-abu asteroid
    # Hits 3: Utuh, Hits 2: Retak Sedang, Hits 1: Retak Parah
    COLORS = {3: '#596275', 2: '#718093', 1: '#b2bec3'}

    def __init__(self, canvas, x, y, hits):
        self.width = 70
        self.height = 30
        self.hits = hits
        self.center_x = x
        self.center_y = y

        # Membuat bentuk dasar polygon agar menyerupai batu asteroid yang tidak beraturan
        points = self.get_asteroid_points(x, y, hits)
        color = Brick.COLORS[hits]

        item = canvas.create_polygon(points, fill=color, outline='#2f3640', width=2, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def get_asteroid_points(self, cx, cy, hits):
        w = self.width / 2
        h = self.height / 2
        
        # Variasi bentuk berdasarkan sisa hit (semakin sedikit hit/semakin rusak, bentuk makin tidak beraturan/kecil)
        if hits == 3:
            return [
                cx - w + 5, cy - h + 2,
                cx + w - 8, cy - h - 3,
                cx + w + 2, cy + h - 5,
                cx - w + 10, cy + h + 2,
                cx - w - 2, cy
            ]
        elif hits == 2:
            return [
                cx - w + 12, cy - h + 5,
                cx + w - 10, cy - h + 2,
                cx + w - 2, cy + h - 8,
                cx - w + 8, cy + h - 2,
                cx - w + 2, cy - 2
            ]
        else: # hits == 1 (Retak parah/pecahan kecil)
            return [
                cx - w + 18, cy - h + 8,
                cx + w - 15, cy - h + 6,
                cx + w - 8, cy + h - 10,
                cx - w + 12, cy + h - 6
            ]

    def get_position(self):
        # Mengembalikan bounding box perkiraan dari polygon untuk sistem deteksi tabrakan canvas.find_overlapping
        return self.canvas.bbox(self.item)

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.delete()
        else:
            # Update bentuk asteroid menjadi lebih kecil/rusak dan ubah warnanya
            new_points = self.get_asteroid_points(self.center_x, self.center_y, self.hits)
            self.canvas.coords(self.item, *new_points)
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])


class Game(tk.Frame):

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400

        self.canvas = tk.Canvas(
            self, bg='#0b0d1b', width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        self.draw_stars()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        
        # Menyusun posisi asteroid (menggantikan balok brick)
        for x in range(15, self.width - 15, 75):
            self.add_brick(x + 35, 50, 3)
            self.add_brick(x + 35, 85, 2)
            self.add_brick(x + 35, 120, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-15))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(15))

    def draw_stars(self):
        for _ in range(80):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height)
            size = random.choice([1, 1, 2])
            star_color = random.choice(['#ffffff', '#d1d8e0', '#a5b1c2'])
            self.canvas.create_oval(
                sx,
                sy,
                sx + size,
                sy + size,
                fill=star_color,
                outline=star_color,
            )

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='25'):
        font = ('Arial', size, 'bold')
        return self.canvas.create_text(x, y, text=text, font=font, fill='white')

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.draw_text(300, 200, 'You win!')
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose!!! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Space Breakout Game')
    game = Game(root)
    game.mainloop()
