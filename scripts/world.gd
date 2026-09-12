extends Node2D

func _ready() -> void:
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 2600, 1080), Color("#071027"))
	draw_circle(Vector2(1580, 150), 70, Color("#cad8ff"))
	draw_circle(Vector2(1610, 130), 68, Color("#071027"))

	for i in range(13):
		var x := float(i * 205)
		var height := float(270 + (i % 5) * 70)
		var top := 900.0 - height
		var building_color := Color("#0c1834") if i % 2 == 0 else Color("#111d3d")
		draw_rect(Rect2(x, top, 190, height), building_color)

		for row in range(3, int(height / 65.0)):
			for column in range(1, 5):
				var wp := Vector2(x + column * 35.0, top + row * 52.0)
				var c := Color("#ffcb65")
				if (row + column + i) % 4 == 0:
					c = Color("#142651")
				draw_rect(Rect2(wp, Vector2(17, 25)), c)

	draw_rect(Rect2(0, 860, 2600, 220), Color("#111522"))
	draw_rect(Rect2(0, 900, 2600, 15), Color("#252b3b"))

	for x in range(0, 2600, 220):
		draw_rect(Rect2(x + 35, 985, 120, 10), Color("#c9c7a4"))
		draw_line(Vector2(x + 60, 920), Vector2(x + 100, 1060), Color(0.1, 0.55, 0.8, 0.18), 18)

	for i in range(85):
		var rx := float((i * 173) % 2500)
		var ry := float((i * 97) % 850)
		draw_line(Vector2(rx, ry), Vector2(rx - 14, ry + 35), Color(0.42, 0.72, 1.0, 0.24), 2)
