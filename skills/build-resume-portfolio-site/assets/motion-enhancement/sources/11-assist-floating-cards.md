---
source_id: 11-assist-floating-cards
original_number: 10
usage_scope: motion-recipe-source-only
---

10、# High-Fidelity Front-End Engineering Prompt: "Assist." Hero Landing Page

You are an award-winning web developer. Use this comprehensive development blueprint and visual style guide to generate or rebuild an exact, modern, ultra-high-fidelity interactive landing page with a responsive dual-column grid, fluid micro-animations, and custom liquid-glass panels.

---

## 1. Visual Identity & Mood
* **Design Philosophy**: Minimalist, tech-forward corporate, eye-safe high-contrast light theme with luxurious negative space, balanced margins, and premium smooth interfaces (squircle roundings, translucent borders, and subtle glowing backdrops).
* **Color Palette**:
  * **Core Canvas**: Solid white (`#FFFFFF`) with ambient subtle glows.
  * **Brand Primary**: Electric Blue (`#0084FF`) and dark active gradient equivalents (`#0074E0`, `#0066CC`).
  * **Rich Black text**: `#000000` for display headings, dark neutral `#171717` (neutral-900) for body, and readable desaturated gray `#6B7280` (neutral-500) for caption states.
  * **Background Ambient Aura**: Translucent radial spotlights of Soft Sky Blue (`#60B1FF` at 20% opacity) and Vibrant Electric Blue (`#319AFF` at 20% opacity) with heavy gaustian blurs (`blur-[100px]` to `blur-[120px]`).
  * **Liquid Glass Properties**: Custom gradients blending `from-white/75` to `to-white/45` with a backdrop filter blur of `20px` to `50px`, a crisp `border-white/70`, and light inset highlight rings mimicking refracted reflections.

---

## 2. Typography & Font Selection Setup
Import and declare the following custom typography assets locally in your CSS entrypoint:
* **Display Font (Headings)**: `Outfit` (font Weights: 400, 500, 600, 700, 800, 900)
  * Set `--font-outfit: "Outfit", sans-serif;`
* **Brand Font (Logo)**: `Fustat` (font Weights: 500, 600, 700, 800)
  * Set `--font-fustat: "Fustat", sans-serif;`
* **Body & Interface Font**: `Inter` (font Weights: 400, 500, 600, 705)
  * Set `--font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;`
* **Aesthetic Adjustments**:
  * Display titles must use `tracking-[-3px]` or `tracking-tight` with tight line heights (`leading-[1.08]`) to establish deep editorial rhythms.
  * Body copy must use generous heights (`leading-relaxed`) and subtle tight adjustments (`tracking-[-0.5px]`).

---

## 3. Structural Wireframe & Responsiveness
* **Width Containment**: The central responsive wrapper is limited to a maximum width of `1280px` (`w-full max-w-[1280px] mx-auto`) with responsive padding settings: `px-6 sm:px-12 lg:px-20 pt-[80px] md:pt-[80px]`.
* **Rethinking Grid Columns**: Under `lg` breakpoint (`1024px`), stack elements vertically in 1 column (`grid-cols-1`). On desktop (`lg:` upward), transition to a balanced 12-column grid (`grid-cols-12`) with a gap of `gap-10 lg:gap-12` where:
  * **Left Column**: occupies 5 columns (`lg:col-span-5`).
  * **Right Column**: occupies 7 columns (`lg:col-span-7`).

---

## 4. Complete Component Implementations

### A. Floating Liquid-Glass Navigation Bar
* **Position**: Sticky pinned near the top of the browser window (`fixed top-[30px] left-0 right-0 z-50 flex justify-center px-4 pointer-events-none`).
* **Frame Coordinates**: A full-width liquid container (`w-full h-12 rounded-[16px] pointer-events-auto transition-all duration-300`). Transparent background, no borders, no box-shadows.
* **Inner Layout**: Flat items with spaced alignments (`flex items-center justify-between gap-8 px-6 py-2 w-full`):
  1. **Brand Logo**: Uses font Fustat ExtraBold (`text-[22px] tracking-tight text-black flex items-center gap-2`). Incorporate a `Bot` icon from `lucide-react` (`w-6 h-6 text-[#0084FF]`) beside the branding text `"Assist."`.
  2. **Inter Links**: Desktop-only navigation list containing `"Home"`, `"Features"`, `"Company"`, and `"Pricing"`. Style as `text-[14px] font-medium text-black/60 hover:text-black transition-colors`.
  3. **Call-to-Action**: A mini premium pill selector styled like a tactile button (`group h-9 px-5 rounded-[12px] bg-black/5 hover:bg-black/10 border border-black/10 text-[14px] font-semibold flex items-center gap-2 text-black transition-all hover:shadow-md`). Append a trailing small right arrow (`ArrowRight` from lucide icon pack, sizing `w-3.5 h-3.5`).
* **Mobile Handling**: Under `md`, replace navigation links with a minimalist Menu trigger. Clicking the menu slides in a solid sliding white responsive drawer from the right edge (`w-[260px] bg-white/95 backdrop-blur-[40px] border-l border-black/10`), containing the relative links vertically structured.

### B. Left Column: Copy, Social Proof & CTAs
* **Container Limits**: Spacing metrics set as `flex flex-col justify-center items-start text-left max-w-[620px] lg:pr-6`.
* **Social Proof Badge (Top item)**:
  * **Structure**: Rounded organic capsule (`px-3 py-1.5 rounded-full bg-black/5 border border-black/5 flex items-center gap-3 w-fit shadow-xs`).
  * **User Avatar Collage**: Four layered Unsplash face profile cards overlap slightly on the negative horizontal axis (`flex -space-x-2 select-none`). Use these matching absolute URLs:
    1. `https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&h=80&fit=crop&crop=face` (Fem)
    2. `https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face` (Masc)
    3. `https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=80&h=80&fit=crop&crop=face` (Fem)
    4. `https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&h=80&fit=crop&crop=face` (Masc)
    * Size each avatar as `w-6 h-6 rounded-full border-1.5 border-white object-cover`.
  * **Text Details**: `"Trusted by 10,000+ users worldwide"` in Inter Regular (`text-[12px] text-black/80`). Bold the words `"10,000+ users"` with `#171717` (neutral-900).
* **Main Display Heading**:
  * Copy: `"Your All in One <br/> Assist."`
  * Styles: Large display typography using Outfit Black, `text-[36px] sm:text-[44px] lg:text-[60px] leading-[1.08] tracking-[-3px] mt-6 select-none text-black`.
* **Body Paragraph**:
  * Copy: `"Ask questions, get answers, automate tasks, and boost your productivity with the power of AI."`
  * Styles: Rounded Inter Regular, `text-[18px] text-black/60 tracking-[-0.5px] leading-relaxed mt-5 max-w-[480px]`.
* **Button Container**: Flex stack (`mt-8 flex flex-wrap items-center gap-6`). Contains:
  1. **Primary Button ("Try Assist.")**:
     * Visual style: Vibrant blue (`bg-[#0084FF] hover:bg-[#0074E0] text-white`). Highly padded responsive layout (`pl-6 pr-2 py-2 rounded-[16px] flex items-center gap-4 text-sm font-bold transition-all w-fit shadow-lg`).
     * Reflection Highlight: Native shadow formula: `box-shadow: inset 0px 4px 4px 0px rgba(255,255,255,0.35), 0 10px 25px -5px rgba(0, 132, 255, 0.25)`.
     * Trailing Icon: A small solid round white bead (`w-8 h-8 rounded-full bg-white flex items-center justify-center text-[#0084FF]`). Contains a right Chevron vector.
  2. **Watch Demo Video Link**:
     * Visual style: Ghost interactive layout (`flex items-center gap-2 group`). Contains a left play arrow bead (`w-9 h-9 rounded-full bg-blue-50 group-hover:bg-blue-100 flex items-center justify-center border border-blue-100 transition-colors`). Play icon must use `#0084FF`.
     * Text: `"Watch Demo"` in Inter Bold (`text-[14px] text-[#0084FF] group-hover:text-[#0074E0] transition-colors`).

### C. Right Column: Hero Robot Companion video & Floating Tags
* **Placement Bounds**: Padded structure (`relative w-full flex items-center justify-center lg:justify-end py-10 pointer-events-none`).
* **Decorative Orbit Art**:
  * An absolute background aura circle: `top-[30%] left-[20%] w-[420px] h-[420px] bg-sky-400/15 rounded-full blur-[110px] -z-10 animate-pulse duration-[7000ms]`.
  * Absolute thin orbital concentric ring lines using a fast vector blueprint: `w-[620px] h-[620px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-[52%] -z-10 opacity-35`. Inside, draw custom path vectors with sky gradients (`#60B1FF`, `#319AFF`) and light dash-array patterns.
* **Centered Robot Companion Video**:
  * Original asset MP4 link: `https://strvid.nyc3.cdn.digitaloceanspaces.com/motionsite/hero_robo_video.mp4`
  * Frame parameters: Full width bounding box inside a `max-w-[600px]` wrapper, height `auto`, high-contrast rounded borders (`rounded-[24px] select-none block`). Keep it pure, raw, and authentic without background patches or shadow covers. Use a custom CSS inline filter style `filter: brightness(1.02) contrast(1.04)` to seamlessly blend the video white background with the main parent container background. Include attributes: `autoPlay`, `loop`, `muted`, `playsInline`, `controls={false}`.
* **Dynamic Floating Badges**:
  Three custom-crafted liquid-glass tasking cards suspended around the companion robot via relative coordinates. All cards inherit:
  * Glass gradient background: `bg-gradient-to-br from-white/75 to-white/45`
  * Dual-ring border layer: `border border-white/70 ring-1 ring-black/5 (or themed colored ring)`
  * Translucent backing: `backdrop-blur-[20px]`
  * Light offset highlights: `shadow-[nested inset_0_2.5px_4px_rgba(255,255,255,0.8)]`

  #### 1. "Write an email" Badge (Suspended Top Right)
  * **Anchors**: `absolute top-[18%] -right-4 sm:-right-10 md:-right-14`.
  * **Visual Style**: Fitted box with spring properties (`px-5 py-3 rounded-[20px] flex items-center gap-3 pointer-events-auto shadow-[0_12px_32px_-4px_rgba(0,132,255,0.12)]`).
  * **Icon Aspect**: Left flat bead (`w-8 h-8 rounded-xl bg-gradient-to-br from-[#0084FF] to-[#0066CC] flex items-center justify-center shadow-[0_4px_12px_rgba(0,132,255,0.3)]`). Inside, hold a white Pen line icon (`PenLine` from lucide).
  * **Text Alignment**: Stacked text column (`flex flex-col text-left leading-tight`):
    * Primary: `"Write an email"` (Inter Black, `text-[13px] text-neutral-900 tracking-tight`).
    * Secondary: `"for meeting"` (Inter SemiBold, `text-[10px] text-neutral-500 mt-0.5`).

  #### 2. "Summarize document" Badge (Suspended Center Left)
  * **Anchors**: `absolute top-[48%] -left-6 sm:-left-12 md:-left-16`.
  * **Visual Style**: Fitted box with spring properties (`px-5 py-3 rounded-[20px] flex items-center gap-3 pointer-events-auto shadow-[0_12px_32px_-4px_rgba(16,185,129,0.12)]`).
  * **Icon Aspect**: Left flat green bead (`w-8 h-8 rounded-xl bg-gradient-to-br from-[#10B981] to-[#059669] flex items-center justify-center shadow-[0_4px_12px_rgba(16,185,129,0.3)]`). Inside, hold a white Document line icon (`FileText` from lucide).
  * **Text Alignment**: Stacked text column (`flex flex-col text-left leading-tight`):
    * Primary: `"Summarize"` (Inter Black, `text-[13px] text-neutral-900 tracking-tight`).
    * Secondary: `"this document"` (Inter SemiBold, `text-[10px] text-neutral-500 mt-0.5`).

  #### 3. "Create a to-do list" Badge (Suspended Bottom Right)
  * **Anchors**: `absolute bottom-[18%] -right-4 sm:-right-8 md:-right-12`.
  * **Visual Style**: Fitted box with spring properties (`px-5 py-3 rounded-[20px] flex items-center gap-3 pointer-events-auto shadow-[0_12px_32px_-4px_rgba(147,51,234,0.12)]`).
  * **Icon Aspect**: Left flat purple bead (`w-8 h-8 rounded-xl bg-gradient-to-br from-[#9333EA] to-[#7E22CE] flex items-center justify-center shadow-[0_4px_12px_rgba(147,51,234,0.3)]`). Inside, hold a white check icon (`Check` with `stroke-[3px]` from lucide).
  * **Text Alignment**: Stacked text column (`flex flex-col text-left leading-tight`):
    * Primary: `"Create a to-do list"` (Inter Black, `text-[13px] text-neutral-900 tracking-tight`).
    * Secondary: `"for today"` (Inter SemiBold, `text-[10px] text-neutral-500 mt-0.5`).



## 5. Micro-Animations Blueprint

* **Entrance Animations**:
  * Core header & navbar: Slide down from `-20px` to `0` with a smooth ease-out curve (`ease: [0.16, 1, 0.3, 1]`) spanning `0.6s`.
  * Left Hero text container and Right companion frame: Slide up from `20px` to `0` with a slow spring overlay spanning `0.9s` matching sequence delay.
  * Floating Cards: Entrance animation with a swift spring preset (`type: "spring", damping: 20, stiffness: 100`) staggered from `0.6s` to `1.0s` delay.
* **Persistent Looping Float Animations (The "Breathing" Effect)**:
  Apply subtle, asynchronous sine-wave translations to the suspended cards so they appear to float weightlessly:
  * **Email Card (Top Right)**: Floats up and down on the Y-axis by `8px` and translates on X-axis by `2px` over a `5.0-second` loop duration (`ease: "easeInOut"`). On hover, scales by `5%`, rotates by `1deg`.
  * **Summarize Card (Center Left)**: Floats down and up on the Y-axis by `8px` and shifts on X-axis by `-2px` over a `5.5-second` loop duration (`ease: "easeInOut"`). On hover, scales by `5%`, rotates by `-1deg`.
  * **To-Do Card (Bottom Right)**: Floats up and down on the Y-axis by `10px` and translates on X-axis by `-1px` over a sequential `4.8-second` loop duration (`ease: "easeInOut"`). On hover, scales by `5%`, rotates by `1.5deg`.
* **State Interlocking (Hover Feedbacks)**:
  * Overlapping customer avatars expand outwards slightly on hover.
  * The primary CTA button uses a spring hover transition (`whileHover: { scale: 1.02 }`, `whileTap: { scale: 0.98 }`). The inner round white chevron circle translates to the right dynamically on state active.
  * Technology footer cards tilt slightly upwards (`hover:translate-y-[-2px] hover:scale-[1.02]`) with the background squircles scaling outwards dynamically (`hover:scale-110`).
