#version 120

varying vec2 v_position;
uniform float u_fov = 0.1f;
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

	vec2 uv = vec2(X*0.2f+0.5f,Y*0.2f+0.5f);
	float scale = 1.f; //512 / 512;
	uv=((uv-0.5f)*5.5);
	uv.y*=scale;
	//uv.y+=0.f;
	uv.x-=0.5f;

	vec2 z = vec2(0.0, 0.0);
	vec3 c = vec3(0.0, 0.0, 0.0);
	float v;

	float I=0.f;
	for(int i=0;(i<80-t*25);i++)
	{
		if(((z.x*z.x+z.y*z.y) >= 4.f)) return vec4(c.r,c.b,0.f,0.f);
		z = vec2(z.x*z.x - z.y*z.y, 2.0*sin((t*2.f+u_timer)*0.5f)*z.y*z.x) + uv;
		if((z.x*z.x+z.y*z.y) >= 2.f)
		{
			c.b=float(i)/20.0;
			c.r=0.5f+0.5f*sin(float(i)/5.0);
		}
		I += 1.f+cos(u_timer);
	}
	if(I>Z)
		return vec4(c.r,c.b,0.f,1.0);
	else
		return vec4(0.f,0.f,c.r,0.f);
}

vec4 julia_on_fire( vec3 o, vec3 d, float t)
{
	float X = o.x + d.x * t;
	float Y = o.y + d.y * t;
	float Z = o.z + d.z * t;

    vec2 z;
    z.x = 3.f * X;
    z.y = 2.f * Y;

    int i;
    for(i=0; i<20; i++) {
        float x = cos(u_timer+t) + (z.x * z.x - z.y * z.y) + d.x;
        float y = sin((u_timer+t*0.5f)*1.5) + (z.y * z.x + z.x * z.y) + d.y;

        if((x*x + y*y) > 4.0) return vec4(0.f,0.f,0.f,0.f);
        z.x = x;
        z.y = y;
    }
    return vec4(0.5f+z.x,0.5f+z.y,z.x,0.f);
}

vec4 julia( vec3 o, vec3 d, float t)
{
	float X = o.x + d.x * t;
	float Y = o.y + d.y * t;
	float Z = o.z + d.z * t;

    vec2 z;
    z.x = 2.f * X + cos(2.2f*u_timer+t);
    z.y = 2.f * Y + sin(u_timer+t);

    int i;
    for(i=0; i<50; i++) {
        float x = (z.x * z.x - z.y * z.y) + d.x;
        float y = (z.y * z.x + z.x * z.y) + d.y;

        if((x*x + y*y) > 4.0) return vec4(0.f,0.f,0.f,0.f);
        z.x = x;
        z.y = y;
    }
    return vec4(0.5f+z.x,0.5f+z.y,z.x,0.f);
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
    //origin.z += u_timer;
    origin = rotate( origin, rotationCenter, angles );

	vec3 dir = (vec3(u_origin.x+pos.x, u_origin.y+pos.y, u_origin.z+u_fov));
    //dir.z += u_timer;
    dir = rotate( dir, rotationCenter, angles );

	bool found=false;
	vec4 color = vec4(0.f,0.f,0.f,0.f);
    float d=0.f;
    for( float t=10.f; t>=0.5f; t-=0.1f)
    {
    	if(false) {
			if( wave(origin, dir, t) ) {
				d += t-d;
				color += 0.05f*vec4(d/100.f,0,0,1.f);
			}
		}
		else
		{
    		//color += 0.2f*calc_mandel(origin, dir, t)/t;
    		color += 0.8f*julia(origin, dir, t)/t;
    	}
    }
    gl_FragColor = color;
}
