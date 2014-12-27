#version 120

varying vec2 v_position;
uniform float u_fov = 0.0;
uniform float u_timer = 0.0;
uniform vec3 u_origin = vec3( 0.f, 0.f, -4.f );
uniform float u_rotation_x = 0.0;
uniform float u_rotation_y = 0.0;
uniform float u_rotation_z = 0.0;

vec3 rotate( in vec3 source, in vec3 rotationCenter, in vec3 angles )
{
	vec3 cosAngles = vec3( cos(angles.x), cos(angles.y), cos(angles.z));
	vec3 sinAngles = vec3( sin(angles.x), sin(angles.y), sin(angles.z));

	// Rotate Center
	vec3 vector = source - rotationCenter;
	vec3 result = vector;

	/* X axis */
	result.y = vector.y*cosAngles.x - vector.z*sinAngles.x;
	result.z = vector.y*sinAngles.x + vector.z*cosAngles.x;
	vector = result;
	result = vector;

	/* Y axis */
	result.z = vector.z*cosAngles.y - vector.x*sinAngles.y;
	result.x = vector.z*sinAngles.y + vector.x*cosAngles.y;
	vector = result;
	result = vector;

	/* Z axis */
	result.x = vector.x*cosAngles.z - vector.y*sinAngles.z;
	result.y = vector.x*sinAngles.z + vector.y*cosAngles.z;

	return result+rotationCenter;
}

vec4 calc_mandel(vec3 o, vec3 d, float t)
{
	float X = o.x + d.x * t;
	float Y = o.y + d.y * t;
	float Z = o.z + d.z * t;

	vec2 uv = vec2(X*0.1f+0.5f,Y*0.1f+0.5f);
	float scale = 1.f; //512 / 512;
	uv=((uv-0.5f)*5.5);
	uv.y*=scale;
	//uv.y+=0.f;
	uv.x-=0.5f;

	vec2 z = vec2(0.0, 0.0);
	vec3 c = vec3(0.0, 0.0, 0.0);
	float v;

	float I=0.f;
	for(int i=0;(i<100-t*25);i++)
	{
		if(((z.x*z.x+z.y*z.y) >= 4.f)) break;
		z = vec2(z.x*z.x - z.y*z.y, 2.0*sin((t+u_timer)*0.5f)*z.y*z.x) + uv;
		if((z.x*z.x+z.y*z.y) >= 2.f)
		{
			c.b=float(i)/20.0;
			c.r=0.5f+0.5f*sin(float(i)/5.0);
		}
		I += 1.f+cos(u_timer);
	}
	if(I>Z)
		return vec4(c.b,c.r,0.f,1.0);
	else
		return vec4(0.f,0.f,c.r,0.f);
}

bool wave( vec3 o, vec3 d, float t )
{
	float x = o.x + d.x * t;
	float y = o.y - d.y * t;
	float z = o.z + d.z * t;
	float h = 0.5f*cos(x+sin(z)+u_timer)*sin(z*4.f+cos(x)) + 1.f;
	return (y<h);
}

void main()
{
	vec3 rotationCenter = vec3(0.f,0.f,0.f);
	vec3 angles = vec3(u_rotation_x,u_rotation_y,u_rotation_z);
    vec2 pos = v_position;
    vec3 origin = u_origin;
    origin.z = u_fov;
    origin = rotate( origin, rotationCenter, angles );
    vec3 dir = (vec3(pos.x, pos.y, u_fov+2.f)-origin);
    dir = rotate( dir, rotationCenter, angles );

	bool found=false;
	vec4 color = vec4(0.f,0.f,0.f,0.f);
    float d=0.f;
    for( float t=1.f; t<3.f; t+=.5f)
    {
    	if(false) {
			if( wave(origin, dir, t) ) {
				d += t-d;
				color += 0.2f*vec4(d/100.f,0,0,1.f);
			}
		}
		else
    		color += 0.6f*calc_mandel(origin, dir, t)/t;
    }
    gl_FragColor = color;
}
