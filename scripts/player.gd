extends CharacterBody2D

const ANIMATION_FPS := 15.0

@export var speed: float = 430.0
@export var jump_velocity: float = -900.0
@export var gravity: float = 2300.0
@export var maximum_health: int = 100

var health: int = 100
var ammunition: int = 12
var maximum_ammunition: int = 12
var facing: int = 1

var attack_locked: bool = false
var invulnerable: bool = false
var action_name: String = "idle"
var animation_time: float = 0.0

func _ready() -> void:
	add_to_group("player")
	health = maximum_health

	var collision := CollisionShape2D.new()
	var shape := CapsuleShape2D.new()
	shape.radius = 37
	shape.height = 170
	collision.shape = shape
	collision.position = Vector2(0, -5)
	add_child(collision)

	var camera := Camera2D.new()
	camera.position = Vector2(280, -170)
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 7.0
	camera.limit_left = 0
	camera.limit_right = 2600
	camera.limit_top = 0
	camera.limit_bottom = 1080
	add_child(camera)

	Tilt.calibrate()
	queue_redraw()

func _physics_process(delta: float) -> void:
	animation_time += delta

	if not is_on_floor():
		velocity.y += gravity * delta

	var axis := Tilt.get_move_axis(delta)

	# PC test
	var keyboard_axis := 0.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		keyboard_axis -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		keyboard_axis += 1.0
	if keyboard_axis != 0.0:
		axis = keyboard_axis

	if not attack_locked:
		velocity.x = axis * speed
		if abs(axis) > 0.08:
			facing = 1 if axis > 0 else -1
			action_name = "run"
		else:
			action_name = "idle"
	else:
		velocity.x = move_toward(velocity.x, 0.0, 1800.0 * delta)

	if not is_on_floor():
		action_name = "jump"

	move_and_slide()
	queue_redraw()

func action(kind: String) -> void:
	match kind:
		"jump":
			if is_on_floor() and not attack_locked:
				velocity.y = jump_velocity
				action_name = "jump"

		"punch":
			if not attack_locked:
				action_name = "punch"
				_melee_attack(150.0, 20)
				_lock_action(0.34)

		"kick":
			if not attack_locked:
				action_name = "kick"
				_melee_attack(205.0, 28)
				_lock_action(0.46)

		"dodge":
			if not attack_locked:
				action_name = "dodge"
				invulnerable = true
				velocity.x = facing * 850.0
				_lock_action(0.32, true)

		"shoot":
			if not attack_locked and ammunition > 0:
				ammunition -= 1
				action_name = "shoot"
				_ranged_attack()
				_lock_action(0.27)

		"reload":
			if not attack_locked and ammunition < maximum_ammunition:
				action_name = "reload"
				_reload_action()

func _melee_attack(distance: float, damage: int) -> void:
	for enemy in get_tree().get_nodes_in_group("enemy"):
		if not is_instance_valid(enemy):
			continue
		var d: Vector2 = enemy.global_position - global_position
		var correct_dir := sign(d.x) == facing
		if abs(d.x) <= distance and abs(d.y) <= 120.0 and correct_dir:
			if enemy.has_method("take_damage"):
				enemy.take_damage(damage)

func _ranged_attack() -> void:
	for enemy in get_tree().get_nodes_in_group("enemy"):
		if not is_instance_valid(enemy):
			continue
		var d: Vector2 = enemy.global_position - global_position
		var correct_dir := sign(d.x) == facing
		if correct_dir and abs(d.x) < 800.0 and abs(d.y) < 150.0:
			if enemy.has_method("take_damage"):
				enemy.take_damage(35)
				break

func _lock_action(seconds: float, dodge: bool = false) -> void:
	attack_locked = true
	await get_tree().create_timer(seconds).timeout
	attack_locked = false
	if dodge:
		invulnerable = false

func _reload_action() -> void:
	attack_locked = true
	await get_tree().create_timer(0.8).timeout
	ammunition = maximum_ammunition
	attack_locked = false

func take_damage(amount: int) -> void:
	if invulnerable or health <= 0:
		return
	health = max(health - amount, 0)
	invulnerable = true
	action_name = "damage"
	await get_tree().create_timer(0.45).timeout
	invulnerable = false
	if health <= 0:
		health = maximum_health
		global_position = Vector2(350, 800)

func _draw() -> void:
	var bob := 0.0
	if action_name == "run":
		var frame := int(animation_time * ANIMATION_FPS) % 6
		bob = -4.0 if frame % 2 == 0 else 2.0

	var body := Color("#f2f0ec")
	var skin := Color("#d97a48")
	var pants := Color("#1651a1")
	var outline := Color("#091020")
	if invulnerable:
		body = Color("#ff7189")

	draw_ellipse(Vector2(0, 87), Vector2(52, 13), Color(0, 0, 0, 0.38))
	draw_line(Vector2(-17, 20 + bob), Vector2(-30, 78), outline, 34)
	draw_line(Vector2(-17, 20 + bob), Vector2(-30, 78), pants, 25)
	draw_line(Vector2(17, 20 + bob), Vector2(32, 78), outline, 34)
	draw_line(Vector2(17, 20 + bob), Vector2(32, 78), pants, 25)

	draw_rect(Rect2(-40, -62 + bob, 80, 90), outline)
	draw_rect(Rect2(-33, -57 + bob, 66, 80), body)

	draw_circle(Vector2(0, -92 + bob), 32, outline)
	draw_circle(Vector2(0, -88 + bob), 26, skin)
	draw_line(Vector2(-22, -94 + bob), Vector2(22, -94 + bob), outline, 5)

	if action_name in ["punch", "shoot"]:
		var reach := 95.0 if action_name == "punch" else 125.0
		draw_line(Vector2(facing * 25, -40 + bob), Vector2(facing * reach, -45 + bob), outline, 23)
		draw_line(Vector2(facing * 25, -40 + bob), Vector2(facing * reach, -45 + bob), skin, 15)
	else:
		draw_line(Vector2(-27, -40 + bob), Vector2(-48, 5 + bob), outline, 22)
		draw_line(Vector2(27, -40 + bob), Vector2(48, 5 + bob), outline, 22)

	if action_name == "kick":
		draw_line(Vector2(facing * 10, 25), Vector2(facing * 115, 12), outline, 34)
		draw_line(Vector2(facing * 10, 25), Vector2(facing * 115, 12), pants, 25)

func draw_ellipse(center: Vector2, radius: Vector2, color: Color) -> void:
	var pts := PackedVector2Array()
	for i in range(33):
		var a := TAU * float(i) / 32.0
		pts.append(center + Vector2(cos(a) * radius.x, sin(a) * radius.y))
	draw_colored_polygon(pts, color)
