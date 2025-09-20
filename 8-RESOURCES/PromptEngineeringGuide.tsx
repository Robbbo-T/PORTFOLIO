/**
 * ASI-T Prompt Engineering Guide - UTCS Reference Snippets
 * UTCS ID: utcs:asi-t:resources:prompt-guide:AT-0001:v1.0.0
 * Owner: Amedeo Pelliccia (© 2024) — Licensed under AQUA-OS Enterprise
 */

// SDXL / Stable Diffusion
const sdxl = `Aerospace operations center, ASI-T "TFA Architecture" core visualized as secure data lattice,
"Quantum Bridge" glow linking CB↔QB, transformer glyphs, satellite & aircraft overlays,
isometric, cinematic lighting, ultradetail --ar 16:9 --stylize 250
NEGATIVE: lowres, watermark, logo, text artifacts, deformed geometry, blurry, extra limbs`;

// Midjourney
const mj = `/imagine prompt: Cockpit HUD view showing "TFA Architecture" trust & governance icons,
a luminous "Quantum Bridge" conduit to quantum nodes, transformer motif, clean UI, aerospace theme --ar 16:9 --v 6 --style raw --chaos 10
--no text, watermark, hands, frames, UI chrome`;

// DALL·E style (natural language)
const dalle = `Create a clean aerospace infographic depicting the "TFA Architecture" core (trust, security, interoperability, governance, DLT) at the center, with a glowing "Quantum Bridge" connecting classical and quantum compute. Include subtle aircraft and satellite silhouettes. Avoid any text labels in the image and keep the style minimalist.`;

// Negative prompt tip
const negativeTip = `Use 'NEGATIVE:' (SDXL) or '--no' (Midjourney) to exclude artifacts; keep negatives short and generic, avoid conflicting constraints.`;

export const ASITPromptGuide = {
  sdxl,
  mj,
  dalle,
  negativeTip,
  
  // Usage examples for consistent ASI-T imagery
  examples: {
    operationsCenter: sdxl,
    cockpitHUD: mj,
    infographic: dalle
  },
  
  // Key terms to include for ASI-T consistency
  keyTerms: [
    "TFA Architecture",
    "Quantum Bridge", 
    "transformer motif",
    "aerospace theme",
    "CB↔QB",
    "secure data lattice"
  ],
  
  // Terms to avoid in prompts
  avoidTerms: [
    "text labels",
    "watermark",
    "UI chrome",
    "hands",
    "deformed geometry"
  ]
};