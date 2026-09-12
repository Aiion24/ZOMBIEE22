extends CharacterBody2D

@export var speed: float = 105.0
@export var maximum_health: int = 70
@export var damage: int = 8

var health: int
var gravity: float = 2300.0
var attack_cooldown: float = 0.0
var hit_flash: bool = false

func _ready() -> void:
	add_to_group("enemy")
	health = maximum_health

	var collision := CollisionShape2D.new()
	var shape := CapsuleShape2D.new()
	shape.radius = 36
	shape.height = 160
	collision.shape = shape
	add_child(collision)

	queue_redraw()

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta

	attack_cooldown = max(attack_cooldown - delta, 0.0)
	var player := get_tree().get_first_node_in_group("player")

	if player and is_instance_valid(player):
		var d: Vector2 = player.global_position - global_position
		if abs(d.x) > 86.0:
			velocity.x = sign(d.x) * speed
		else:
			velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
			if attack_cooldown <= 0.0 and player.has_method("take_damage"):
				player.take_damage(damage)
				attack_cooldown = 0.85

	move_and_slide()
	queue_redraw()

func take_damage(amount: int) -> void:
	health -= amount
	hit_flash = true
	queue_redraw()
	if health <= 0:
		queue_free()
		return
	await get_tree().create_timer(0.12).timeout
	hit_flash = false

func _draw() -> void:
	var skin := Color("#9ab56e")
	var clothes := Color("#5b3049")
	var outline := Color("#130d1d")
	if hit_flash:
		skin = Color("#ff526b")

	draw_circle(Vector2(0, 78), 48, Color(0, 0, 0, 0.3))
	draw_line(Vector2(-14, 20), Vector2(-26, 78), outline, 33)
	draw_line(Vector2(14, 20), Vector2(30, 78), outline, 33)

	draw_rect(Rect2(-38, -56, 76, 82), outline)
	draw_rect(Rect2(-31, -49, 62, 69), clothes)

	draw_circle(Vector2(0, -84), 31, outline)
	draw_circle(Vector2(0, -82), 24, skin)
	draw_circle(Vector2(-9, -87), 4, Color("#ff273b"))
	draw_circle(Vector2(10, -87), 4, Color("#ff273b"))

	draw_line(Vector2(-24, -35), Vector2(-65, -8), outline, 22)
	draw_line(Vector2(24, -35), Vector2(68, -12), outline, 22)
	draw_line(Vector2(-24, -35), Vector2(-65, -8), skin, 14)
	draw_line(Vector2(24, -35), Vector2(68, -12), skin, 14)

	draw_rect(Rect2(-42, -132, 84, 9), Color("#260817"))
	var ratio := clamp(float(health) / maximum_health, 0.0, 1.0)
	draw_rect(Rect2(-42, -132, 84.0 * ratio, 9), Color("#e8324f"))
