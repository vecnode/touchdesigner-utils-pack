#ifndef PI
#define PI 3.1415926535897932384626433832795
#endif

#ifndef DEG2RAD
#define DEG2RAD (PI / 180.0)
#endif

// Custom uniforms — create matching parameters on the GLSL TOP (defaults shown in comments).
uniform float Kaleidonum; // default: 6 — number of kaleidoscope mirrors (clamped to >= 2)
uniform float rotateZ;    // degrees, rotation before folding
uniform float Fullmode;   // 0 = map to ~[0,1] UV; non-zero = scale UV×2 (useful with Repeat on input TOP)

layout(location = 0) out vec4 fragColor;

// width / height; safe if input resolution is unknown or zero
float inputAspect() {
  float w = max(uTD2DInfos[0].res.z, 1.0);
  float h = max(uTD2DInfos[0].res.w, 1.0);
  return w / h;
}

vec2 kaleidoscope(vec2 uv, float n) {
  float wedge = PI / n;
  float r = length(uv * 0.5);
  float a = atan(uv.y, uv.x) / wedge;
  float f = fract(a);
  float m = mod(floor(a), 2.0);
  a = mix(f, 1.0 - f, m) * wedge;
  return vec2(cos(a), sin(a)) * r;
}

// Counter-clockwise rotation by `degrees` (negative angle = clockwise visual spin)
vec2 rotateZDeg(vec2 uv, float degrees) {
  float theta = -degrees * DEG2RAD;
  float c = cos(theta);
  float s = sin(theta);
  return vec2(c * uv.x - s * uv.y, s * uv.x + c * uv.y);
}

void main() {
  float aspect = inputAspect();
  float n = max(Kaleidonum, 2.0);

  vec2 uv = vUV.st * 2.0 - 1.0;
  uv.x *= aspect;

  uv = rotateZDeg(uv, rotateZ);
  uv = kaleidoscope(uv, n);

  // Folded space → sample coordinates (behavior matches original intent)
  if (Fullmode != 0.0) {
    uv *= 2.0;
  } else {
    uv += vec2(0.5);
  }

  uv.x /= aspect;

  fragColor = texture(sTD2DInputs[0], uv);
}
