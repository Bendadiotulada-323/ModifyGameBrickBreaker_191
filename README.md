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

1. Mengubah Latar belakang dari warna unggu menjadi Hitam dengan percikan bintang2 menyerupai latar belakang galaksi luar angkasa
2. Papan diubah warnanya
3. Bentuk Block dirubah menyerupai batu asteroid
4. Batu Asteroid yang dikenai bola dapat hancur sesuai dengan kategori bentuknya ada yang paling lemah dengan 1 hit, 2 hit dan 3 hit sesuai dengan ukuran batunya
5. Bola yang dipantulkan diubah warnanya menjadi warna biru

![alt text](<Screenshot 2026-11-10 110555.png>)
![alt text](<Screenshot 2026-11-10 110611.png>)