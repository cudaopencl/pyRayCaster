#version 120

varying vec3 normal;
attribute vec2 a_position;
varying vec2 v_position;

void main()
{
	normal = gl_NormalMatrix * gl_Normal;
	gl_Position = vec4(a_position, 0.0, 1.0);
	v_position = a_position;
}
