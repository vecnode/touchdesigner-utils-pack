// Feedback Blur Shader
// Combines two input textures using additive blending with opacity control
// Input 0: Base texture
// Input 1: Feedback texture (blurred/processed)
// Output: Maximum blend of both textures, clamped to valid color range

uniform float uOpacity;

out vec4 fragColor;

void main() {
	// Sample input textures
	vec2 uv = vUV.st;
	vec4 baseColor = texture(sTD2DInputs[0], uv);
	vec4 feedbackColor = texture(sTD2DInputs[1], uv);
	
	// Apply opacity to feedback layer
	feedbackColor *= uOpacity;
	
	// Combine using maximum blend (additive-like effect)
	vec4 blendedColor = max(baseColor, feedbackColor);
	
	// Clamp to valid color range [0, 1]
	blendedColor = min(vec4(1.0), blendedColor);
	
	fragColor = blendedColor;
}
