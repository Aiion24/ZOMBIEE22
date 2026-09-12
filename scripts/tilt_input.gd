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
