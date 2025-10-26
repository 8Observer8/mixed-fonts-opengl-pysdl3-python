#ifdef GL_ES
precision mediump float;
#endif

varying vec2 vTexCoord;
uniform vec3 uColor;
uniform vec3 uOutlineColor;
uniform sampler2D uSampler;

const float width = 0.5;
const float edge = 0.1;

const float borderWidth = 0.6;
const float borderEdge = 0.05;

void main()
{
    float distance = 1.0 - texture2D(uSampler, vTexCoord).a; // vec2(vTexCoord.x, 1.0 - vTexCoord.y)
    float alpha = 1.0 - smoothstep(width, width + edge, distance);

    float distance2 = 1.0 - texture2D(uSampler, vTexCoord).a; // vec2(vTexCoord.x, 1.0 - vTexCoord.y)
    float outlineAlpha = 1.0 - smoothstep(borderWidth, borderWidth + borderEdge, distance2);

    float overallAlpha = alpha + (1.0 - alpha) * outlineAlpha;
    vec3 overallColor = mix(uOutlineColor, uColor, alpha / overallAlpha);

    if (overallAlpha < 0.01)
    {
        discard;
    }

    gl_FragColor = vec4(overallColor, overallAlpha);
}
