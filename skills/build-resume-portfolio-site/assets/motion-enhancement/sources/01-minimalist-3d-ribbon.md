---
source_id: 01-minimalist-3d-ribbon
original_number: 1
usage_scope: motion-recipe-source-only
---

1、# Comprehensive Implementation Specification: Minimalist 3D Hero Experience

## 1. Overview & Architecture
Create a highly interactive, premium single-page hero section with a continuous 3D mathematical sculpture running in the background. The aesthetic is ultra-minimalist, monochromatic, and elegant, prioritizing typography and kinetic motion over complex color palettes.

**Tech Stack & Exact Dependencies:**
- Framework: React 18 + Vite + TypeScript
- Styling: Tailwind CSS v3
- Animation: `framer-motion`
- 3D Rendering: `three`, `@react-three/fiber`, `@react-three/drei`, `three-stdlib`
- Smooth Scrolling: `@studio-freight/react-lenis`
- Icons: `lucide-react`

## 1.1 Required File Structure
```text
/src
  ├── App.tsx
  ├── main.tsx
  ├── index.css
  └── components/
      ├── Navbar.tsx
      ├── Hero.tsx
      ├── ThreeCanvas.tsx
      └── Sculpture.tsx
```

---

## 2. Visual Design System

### 2.1 Color Palette
- **Background Base:** Pure White `#FFFFFF`
- **Foreground Base:** Pure Black `#000000`
- **Primary Text:** Dark Gray `#111827` (`gray-900` in Tailwind)
- **Secondary Text:** Medium Gray `#6B7280` (`gray-500` in Tailwind)
- **Overline/Accent Text:** Light Gray `#9CA3AF` (`gray-400` in Tailwind)
- **Button Base:** Off-Black `#0A0A0A`
- **Glassmorphism Base:** `rgba(255, 255, 255, 0.4)` (`white/40`) to `rgba(255, 255, 255, 0.6)` (`white/60`)

### 2.2 Typography
- **Primary Font Family:** "Plus Jakarta Sans", sans-serif (imported via Google Fonts).
- **Hero Title:** 
  - Size: `6xl` (mobile) to `8xl` (desktop)
  - Weight: Medium (500)
  - Tracking: Tight (`tracking-tight`)
  - Line Height: Extremely tight (`leading-[1.05]`)
- **Overlines & Micro-copy:**
  - Size: `text-xs` (12px) to `text-[10px]`
  - Weight: Bold (700) or Semibold (600)
  - Tracking: Wide (`tracking-[0.2em]`)
  - Transform: Uppercase
- **Body Text:**
  - Size: `text-lg` to `text-xl`
  - Weight: Light (300)
  - Line Height: Relaxed (`leading-relaxed`)

---

## 3. UI Components & Layout Hierarchy

### 3.1 Global Layout
- The `main` container is `min-h-screen`, `w-full`, and wraps all components.
- The entire application is wrapped in a `<ReactLenis root>` provider to ensure buttery smooth inertia scrolling across all browsers.
- The 3D Canvas sits in a `fixed inset-0 z-0 pointer-events-none` container behind the normal DOM elements.
- The normal HTML content sits in a `relative z-10 flex flex-col` container that scrolls naturally over the fixed 3D canvas.

### 3.2 Liquid Glass Navbar
- **Position:** Fixed at the top (`z-50`).
- **Initial State (At Top):** Full width (`w-full`), completely transparent background, `pt-8` padding.
- **Scrolled State (`scrollY > 50`):** Shrinks horizontally to `w-[95%] md:w-[80%] max-w-5xl`, centers horizontally, adds `rounded-full` border radius, applies `bg-white/40 backdrop-blur-xl border border-white/50`, adds a subtle shadow (`shadow-[0_8px_32px_rgba(0,0,0,0.08)]`), and reduces padding to `pt-6`.
- **Content:**
  - Left: "GRIDLINE" text logo (tracking wide).
  - Center: Hidden on mobile, flex on desktop. Navigation links (`Home, About, Services, Portfolio, Blog, Contact`). Text is `text-xs font-semibold uppercase tracking-wider text-gray-800 hover:text-black`.
  - Right: A circular hamburger menu button (Lucide `Menu` icon), 48x48px, white background with subtle shadow, slightly transparent on scroll.

### 3.3 Hero Section
- **Position:** Relative, `h-screen`, padding `p-12 pt-32`.
- **Content Structure:** Left-aligned text to allow the 3D sculpture on the right to breathe.
- **Elements:**
  - Overline: "DESIGNING THE FUTURE" (gray-500).
  - Heading: "Where Vision\nMeets Design." (gray-900).
  - Paragraph: "We craft digital experiences that inspire, engage, and elevate your brand." (gray-500, max-width sm).
  - **Buttons Array:**
    - "EXPLORE OUR WORK": Solid dark pill button (`bg-[#0a0a0a]`), rounded-full, `px-8 py-4`, white text (10px, bold, uppercase, tracking-widest). Includes `ArrowUpRight` icon.
    - "Watch Intro": Circular white floating play button with a shadow (`w-14 h-14 bg-white rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.06)]`) holding a black `Play` icon (with `fill-black`), followed by "WATCH INTRO" text.
  - **Bottom Stats Bar:** Positioned at the bottom of the screen (`pb-4`). Displays three statistics horizontally ("200+ Projects", "98% Clients Satisfied", "15+ Awards Won"). Stats numbers are `text-3xl font-medium`, labels are `text-[9px] font-bold tracking-[0.15em] text-gray-400 uppercase`. Separated by 32px vertical lines (`w-px h-8 bg-gray-200`).

---

## 4. 3D Elements & Visual Effects

### 4.1 React Three Fiber Canvas
- The `<Canvas>` should have `shadows`, `gl={{ antialias: true, alpha: true, preserveDrawingBuffer: true }}`, and a white background (`<color attach="background" args={['#ffffff']} />`).
- **Lighting setup (Premium Studio Lighting):**
  - `<ambientLight intensity={1.0} />`
  - Key Light: `<directionalLight position={[10, 20, 15]} intensity={3} color="#ffffff" castShadow />` with high-res shadow maps (2048x2048) and an expanded shadow camera frustum.
  - Fill Lights: Two additional directional lights at `[-10, -10, -10]` (intensity 1.5, `#f8fafc`) and `[0, 0, 15]` (intensity 1.5, white) to eliminate harsh dark spots.
  - `<SoftShadows size={25} samples={10} focus={0.5} />` for incredibly realistic, soft ambient occlusion shadows.

### 4.2 The Mathematical Ribbon Sculpture
- **Concept:** A continuous, twisting ribbon of overlapping rectangular panels flowing in a 3D S-curve shape resembling a large architectural spring.
- **Geometry:** 150 instances of `<RoundedBoxGeometry args={[4, 0.3, 4, 2, 0.02]} />` (width, height, depth, segments, radius).
- **Material:** `<meshPhysicalMaterial color="#ffffff" roughness={0.15} metalness={0.1} clearcoat={1} clearcoatRoughness={0.1} />` to create a glossy, premium ceramic/plastic look.
- **Mathematical Curve Animation:**
  - Managed via an `<InstancedMesh>` with `count={150}`.
  - Inside a `useFrame` loop, the current time is retrieved via `state.clock.getElapsedTime()`.
  - For each instance `i` from 0 to 149:
    - Base offset: `baseT = i / 150`.
    - Animated progression: `t = (baseT + time * 0.003) % 1`.
    - Y-axis (Height span): `y = (0.5 - t) * 22`.
    - X/Z-axis (Spring radius): `springRadius = 3.5`.
    - Coils: 2 full revolutions (`coils = 2`).
    - Angle: `angle = t * Math.PI * 2 * coils`.
    - Position X: `Math.sin(angle) * springRadius + 4` (+4 shifts the entire structure to the right side of the screen so it doesn't block the hero text).
    - Position Z: `Math.cos(angle) * springRadius`.
  - **Orientation & Twisting:**
    - To make the blocks face the path, calculate a tangent point slightly ahead (`t2 = t + 0.001`) and use `dummy.lookAt(target)`.
    - Rotate the blocks 90 degrees on the X-axis (`dummy.rotateX(Math.PI / 2)`) so their large flat face overlaps like a deck of cards.
    - Twist them continuously along the path: `const twist = t * Math.PI * 4 - time * 0.005; dummy.rotateY(twist);`.
  - **Scale Animation:** The blocks scale up from 0 to 1 at the top of the curve, and scale down from 1 to 0 at the bottom to create a seamless infinite loop entry/exit effect.

---

## 5. Animations & Micro-interactions

### 5.1 Framer Motion Reveal Animations
- Use `initial={{ y: 50, opacity: 0 }}` and `animate={{ y: 0, opacity: 1 }}` for entry animations on all text elements and buttons in the Hero.
- Use a custom cubic-bezier easing: `ease: [0.16, 1, 0.3, 1]` (an "out-expo" style very snappy but smooth easing).
- Stagger the delays: Overline (0.2s), Title (0.2s), Paragraph (0.2s), Buttons (0.2s), Stats Bar (0.6s).

### 5.2 Hover States
- "Explore Our Work" button: Background darkens on hover (`hover:bg-gray-800`).
- "Watch Intro" play button: The white circle scales up slightly (`group-hover:scale-105`) and increases drop shadow intensity.
- Navbar Hamburger: Subtle scaling and background color shift.
- Navbar Links: Text color shifts from `text-gray-800` to solid `text-black`.

---

## 6. Implementation Notes & Best Practices

1. **Responsive Design:** 
   - Use Tailwind's `md:` prefixes extensively.
   - For example, Hero Title goes from `text-6xl` (mobile) to `text-[5.5rem]` or `text-8xl` (desktop).
   - Hide the text navigation links on mobile (`hidden md:flex`), leaving only the hamburger menu.
2. **Performance:** 
   - Ensure the 3D `<InstancedMesh>` is used instead of rendering 150 separate meshes, which would cause severe draw-call overhead.
   - Use `useMemo` for the geometries and materials inside the 3D scene to prevent React from re-allocating memory on every render.
3. **Scroll Hijacking:** Do NOT use traditional scroll hijacking. Use `@studio-freight/react-lenis` strictly as a wrapper to preserve native scroll semantics while adding interpolation.
4. **Tailwind Config & CSS:** 
   - `index.css` must hide the scrollbar: `::-webkit-scrollbar { display: none; } * { scrollbar-width: none; }`.
   - `index.css` must include the Google Font import: `@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;500;600;700;800&display=swap');`.
   - Set the default sans font family to `"Plus Jakarta Sans", "Inter", sans-serif`.
