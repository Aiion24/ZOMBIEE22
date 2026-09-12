rom pathlib import Path
import shutil

REPO = Path(".")
GAME_DIR = REPO / "DescontrolZombies"

def write(rel_path: str, content: str):
    p = REPO / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")

# Reemplaza carpeta anterior si existe
if GAME_DIR.exists():
    shutil.rmtree(GAME_DIR)

# .gitignore (solo si no existe)
gitignore = REPO / ".gitignore"
if not gitignore.exists():
    write(".gitignore", r"""
.godot/
.import/
build/
*.apk
*.aab
.DS_Store
Thumbs.db
.vscode/
.idea/
""")

# Proyecto Godot 4.3
write("DescontrolZombies/project.godot", r"""
; DescontrolZombies - Godot 4.3
config_version=5

[application]
config/name="DescontrolZombies"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.3")
config/icon="res://icon.svg"

[autoload]
Tilt="*res://scripts/tilt_input.gd"

[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
window/stretch/mode="canvas_items"
window/stretch/aspect="keep"
window/handheld/orientation=1

[input_devices]
sensors/enable_accelerometer=true
sensors/enable_gravity=true
sensors/enable_gyroscope=true

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
environment/defaults/default_clear_color=Color(0.015, 0.02, 0.06, 1)
""")

# Export preset Android (APK debug)
write("DescontrolZombies/export_presets.cfg", r"""
[preset.0]
name="Android"
platform="Android"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/DescontrolZombies-debug.apk"
script_export_mode=2

[preset.0.options]
custom_template/debug=""
custom_template/release=""
gradle_build/use_gradle_build=true
gradle_build/export_format=0
architectures/armeabi-v7a=false
architectures/arm64-v8a=true
version/code=1
version/name="0.1.0"
package/unique_name="com.descontrol.zombies"
package/name="DescontrolZombies"
package/signed=true
screen/immersive_mode=true
screen/support_small=true
screen/support_normal=true
screen/support_large=true
screen/support_xlarge=true
""")

write("DescontrolZombies/icon.svg", r"""
<svg height="128" width="128" xmlns="http://www.w3.org/2000/svg">
  <rect width="128" height="128" rx="24" fill="#071229"/>
  <circle cx="64" cy="64" r="47" fill="#df1746"/>
  <path d="M32 38h65L48 91h53" fill="none" stroke="#ffffff"
        stroke-width="13" stroke-linejoin="round"/>
</svg>
""")

# Tilt
write("DescontrolZombies/scripts/tilt_input.gd", r"""
extends Node

var sensitivity: float = 0.42
var deadzone: float = 0.08
var smoothing: float = 10.0
var invert: bool = false

var _calibration: float = 0.0
var _filtered_axis: float = 0.0

func _sensor_value() -> float:
	var gravity := Input.get_gravity()
	if gravity.length() > 0.1:
		return gravity.y
	var acceleration := Input.get_accelerometer()
	return acceleration.y

func calibrate() -> void:
	_calibration = _sensor_value()
	_filtered_axis = 0.0

func get_move_axis(delta: float) -> float:
	var raw := (_sensor_value() - _calibration) * sensitivity
	if invert:
		raw = -raw
	if abs(raw) < deadzone:
		raw = 0.0
	raw = clamp(raw, -1.0, 1.0)
	var weight := 1.0 - exp(-smoothing * delta)
	_filtered_axis = lerp(_filtered_axis, raw, weight)
	return _filtered_axis
""")

# World (fondo por código)
write("DescontrolZombies/scripts/world.gd", r"""
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
""")

# Player
write("DescontrolZombies/scripts/player.gd", r"""
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
""")

# Zombie
write("DescontrolZombies/scripts/zombie.gd", r"""
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
""")

# Main spawner
write("DescontrolZombies/scripts/main.gd", r"""
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
""")

# HUD
write("DescontrolZombies/scripts/hud.gd", r"""
extends CanvasLayer

var health_label: Label
var ammo_label: Label
var status_label: Label

func _ready() -> void:
	var ui := Control.new()
	ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(ui)

	health_label = _label(ui, "VIDA: 100", Vector2(45, 35), Vector2(360, 65), 32)
	ammo_label   = _label(ui, "MUNICIÓN: 12/12", Vector2(45, 105), Vector2(360, 60), 27)
	status_label = _label(ui, "Inclina el móvil para moverte", Vector2(650, 35), Vector2(720, 55), 24)

	_btn(ui, "CALIBRAR", Vector2(45, 900), Vector2(230, 105), "calibrate")
	_btn(ui, "SALTAR",   Vector2(300, 900), Vector2(220, 105), "jump")

	_btn(ui, "RECARGA", Vector2(1030, 900), Vector2(205, 105), "reload")
	_btn(ui, "ESQUIVA", Vector2(1250, 820), Vector2(205, 105), "dodge")
	_btn(ui, "DISPARO", Vector2(1470, 900), Vector2(205, 105), "shoot")
	_btn(ui, "PATADA",  Vector2(1690, 780), Vector2(190, 105), "kick")
	_btn(ui, "GOLPE",   Vector2(1690, 920), Vector2(190, 105), "punch")

func _process(_delta: float) -> void:
	var p := get_tree().get_first_node_in_group("player")
	if p:
		health_label.text = "VIDA: %d" % p.health
		ammo_label.text = "MUNICIÓN: %d/%d" % [p.ammunition, p.maximum_ammunition]

func _label(parent: Control, t: String, pos: Vector2, size: Vector2, fs: int) -> Label:
	var l := Label.new()
	l.text = t
	l.position = pos
	l.size = size
	l.add_theme_font_size_override("font_size", fs)
	l.add_theme_color_override("font_color", Color.WHITE)
	l.add_theme_color_override("font_shadow_color", Color.BLACK)
	l.add_theme_constant_override("shadow_offset_x", 3)
	l.add_theme_constant_override("shadow_offset_y", 3)
	parent.add_child(l)
	return l

func _btn(parent: Control, t: String, pos: Vector2, size: Vector2, action: String) -> void:
	var b := Button.new()
	b.text = t
	b.position = pos
	b.size = size
	b.modulate = Color(0.82, 0.92, 1.0, 0.88)
	b.add_theme_font_size_override("font_size", 24)
	b.pressed.connect(func(): _send(action))
	parent.add_child(b)

func _send(action: String) -> void:
	if action == "calibrate":
		Tilt.calibrate()
		status_label.text = "Inclinación calibrada"
		return
	var p := get_tree().get_first_node_in_group("player")
	if p and p.has_method("action"):
		p.action(action)
""")

# Scenes
write("DescontrolZombies/scenes/player.tscn", r"""
[gd_scene load_steps=2 format=3]
[ext_resource path="res://scripts/player.gd" type="Script" id="1"]
[node name="Player" type="CharacterBody2D"]
script = ExtResource("1")
collision_layer = 1
collision_mask = 3
""")

write("DescontrolZombies/scenes/zombie.tscn", r"""
[gd_scene load_steps=2 format=3]
[ext_resource path="res://scripts/zombie.gd" type="Script" id="1"]
[node name="Zombie" type="CharacterBody2D"]
script = ExtResource("1")
collision_layer = 2
collision_mask = 1
""")

write("DescontrolZombies/scenes/main.tscn", r"""
[gd_scene load_steps=8 format=3]
[ext_resource path="res://scripts/main.gd" type="Script" id="1"]
[ext_resource path="res://scripts/world.gd" type="Script" id="2"]
[ext_resource path="res://scripts/hud.gd" type="Script" id="3"]
[ext_resource path="res://scenes/player.tscn" type="PackedScene" id="4"]

[sub_resource type="RectangleShape2D" id="FloorShape"]
size = Vector2(2600, 80)

[node name="Main" type="Node2D"]
script = ExtResource("1")

[node name="World" type="Node2D" parent="."]
script = ExtResource("2")

[node name="Floor" type="StaticBody2D" parent="."]
position = Vector2(1300, 940)
collision_layer = 1
collision_mask = 3

[node name="CollisionShape2D" type="CollisionShape2D" parent="Floor"]
shape = SubResource("FloorShape")

[node name="Player" parent="." instance=ExtResource("4")]
position = Vector2(350, 800)

[node name="HUD" type="CanvasLayer" parent="."]
script = ExtResource("3")
""")

# GitHub Actions (main o master)
write(".github/workflows/android-debug.yml", r"""
name: Generar APK Debug (DescontrolZombies)

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build-android:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Install Android packages
        shell: bash
        run: |
          yes | sdkmanager --licenses >/dev/null || true
          sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

      - name: Create Android debug keystore
        shell: bash
        run: |
          mkdir -p "$HOME/.android"
          if [ ! -f "$HOME/.android/debug.keystore" ]; then
            keytool -genkeypair \
              -keystore "$HOME/.android/debug.keystore" \
              -storepass android \
              -alias androiddebugkey \
              -keypass android \
              -keyalg RSA \
              -keysize 2048 \
              -validity 10000 \
              -dname "CN=Android Debug,O=Android,C=US"
          fi

      - name: Setup Godot 4.3 (with templates)
        uses: chickensoft-games/setup-godot@v2
        with:
          version: "4.3.0"
          use-dotnet: false
          include-templates: true

      - name: Import project (headless)
        shell: bash
        run: |
          cd DescontrolZombies
          godot --headless --editor --quit-after 10

      - name: Export Debug APK
        shell: bash
        run: |
          mkdir -p build
          cd DescontrolZombies
          godot --headless --verbose \
            --export-debug "Android" \
            ../build/DescontrolZombies-debug.apk

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: DescontrolZombies-debug-apk
          path: build/DescontrolZombies-debug.apk
          if-no-files-found: error
          retention-days: 30
""")

write("README_DESCONTROLZOMBIES.md", r"""
# DescontrolZombies (Godot 4.3)
Package: com.descontrol.zombies
APK: debug por GitHub Actions

Sube (push) y ve a Actions -> Generar APK Debug (DescontrolZombies).
""")

print("OK: Se creó DescontrolZombies/ y el workflow de GitHub Actions.")
print("Ahora ejecuta: git add . && git commit -m \"DescontrolZombies\" && git push")
