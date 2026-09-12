extends Node2D
const ZOMBIE_SCENE := preload("res://scenes/zombie.tscn")

var spawn_positions := [Vector2(1120, 805), Vector2(1450, 805), Vector2(1800, 805), Vector2(2200, 805)]

func _ready() -> void:
	randomize()
	for i in range(3):
		_spawn_zombie(spawn_positions[i])

	var timer := Timer.new()
	timer.wait_time = 4.5
	timer.autostart = true
	timer.timeout.connect(_on_spawn_timer)
	add_child(timer)

func _on_spawn_timer() -> void:
	var enemies := get_tree().get_nodes_in_group("enemy")
	if enemies.size() < 4:
		_spawn_zombie(spawn_positions[randi() % spawn_positions.size()])

func _spawn_zombie(pos: Vector2) -> void:
	var z := ZOMBIE_SCENE.instantiate()
	z.global_position = pos
	add_child(z)
