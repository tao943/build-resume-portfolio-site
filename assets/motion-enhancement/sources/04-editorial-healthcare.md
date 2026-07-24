---
source_id: 04-editorial-healthcare
original_number: 4
usage_scope: motion-recipe-source-only
---

4、# MASTER IMPLEMENTATION PROMPT — AI HEALTHCARE SaaS HERO SECTION (LUXURY MINIMAL EDITORIAL STYLE)

Create a premium AI healthcare SaaS hero section. The design should feel elegant, intelligent, trustworthy, futuristic, and minimal while maintaining a luxury editorial aesthetic.

The final experience should feel like a combination of Apple, OpenAI, Stripe, Linear, and a high-end luxury editorial publication.

---

## 1. TECH STACK (MANDATORY)

Build using:
* Vite
* React
* TypeScript
* Tailwind CSS
* Framer Motion
* React Icons

**Core Requirements:**
* Ensure perfect responsive design across mobile, tablet, and desktop (`sm`, `md`, `lg`, `xl` breakpoints).
* Use semantic HTML.
* Organize into reusable React components (Navbar, HeroBadge, HeroHeading, HeroVideo, TrustIndicators, CTAButton).

---

## 2. DESIGN SYSTEM & AESTHETICS

### Color Palette (Precise Hex Codes)
* **Main Background:** `#F5F5F7` (Light, Apple-esque gray)
* **Primary Typography:** `#0A0A0A` (Near black for stark contrast)
* **Secondary Typography:** `#5B5B65` (Sophisticated muted gray)
* **Primary Brand Accent:** `#4F46E5` (Deep Indigo, used sparingly on the logo mark)
* **Borders & Dividers:** `rgba(0, 0, 0, 0.08)`
* **Primary Button Background:** `#111111` or `#0A0A0A` (Text: `#FFFFFF`)
* **Badge/Tag Background:** `rgba(229, 231, 235, 0.5)` with `backdrop-blur-sm`

### Typography
* **Headings:** `Cormorant Garamond` (or similar luxury serif like `Playfair Display`).
  * Weight: `500` (Medium)
  * Line Height: `1.05`
  * Tracking/Letter Spacing: `-0.04em` (Tight, editorial feel)
  * Sizing: `text-[44px]` (Mobile) -> `sm:text-[56px]` -> `md:text-[72px]` -> `lg:text-[96px]` (Desktop).
* **Body/UI:** `Inter` (Clean, geometric sans-serif).
  * Weight: `400` (Regular) and `500` (Medium for UI elements like buttons/nav).
  * Letter Spacing: Tight tracking on UI elements.

---

## 3. LAYOUT & HIERARCHY

### 3.1. Navigation Bar
* **Position:** Fixed to top (`z-50`), full width.
* **Background:** `#F5F5F7/80` with `backdrop-blur-md` and a 1px border bottom `border-[rgba(0,0,0,0.08)]`.
* **Logo Area:** Left-aligned. Text "Aura" (Font: Inter, Medium, `text-xl`). Include an SVG "spark" or modern geometric star icon colored in `#4F46E5`.
* **Desktop Links:** Centered (`hidden md:flex`). Links: "Product", "Story", "Use Cases". `text-sm`, `font-medium`, text `#5B5B65`. Add a 1px black underline that expands on hover (`group-hover:w-full`).
* **Desktop Actions:** Right-aligned. "Sign In" link (hover: opacity 70%) and a solid white "Book a Demo" button with a light black border.
* **Mobile Nav:** Hamburger menu toggle (`react-icons` or SVG). When clicked, slides down a full-screen overlay (`bg-[#F5F5F7]`) powered by `framer-motion` (`AnimatePresence`) displaying the links and a large black CTA button.

### 3.2. Hero Section
* **Spacing:** Padding top `pt-36` or `pt-40` to clear the navbar, `px-6` for mobile padding.
* **Content Alignment:** Center-aligned text and elements. Max-width container to prevent stretching.

### 3.3. Hero Components Top-to-Bottom
1. **Hero Badge:** 
   * Pill shape, inline-flex.
   * Text: "The future of AI in behavioral health" (`text-xs font-medium text-[#5B5B65]`).
   * Styling: `bg-[#E5E7EB]/50`, `backdrop-blur-sm`, `border-[rgba(0,0,0,0.08)]`, rounded full.
2. **Hero Heading:**
   * Text: "Smarter clinical notes.<br />Meet Aura."
   * Styling: Uses the editorial serif font, centered, extremely tight letter spacing.
3. **Hero Subtitle:**
   * Text: "Aura is the advanced AI copilot for healthcare professionals. Streamline your clinical workflows and dedicate more time to delivering exceptional patient care."
   * Styling: `text-lg md:text-xl text-[#5B5B65] leading-relaxed max-w-[700px] mt-8`.
4. **Primary CTA:**
   * Text: "Book a Demo"
   * Styling: Solid black (`#111111`), rounded-xl, padding `px-8 py-4`, `text-white font-medium`.
5. **Hero Video (The Centerpiece):**
   * Video URL: `https://strvid.nyc3.cdn.digitaloceanspaces.com/motionsite/hero_video_head.mp4?utm_source=chatgpt.com`
   * Container Sizing: `max-w-[640px]` wide with an exact aspect ratio of `aspect-[640/594]`.
   * Margins: Negative top margin `mt-6 md:mt-10` to sit tightly under the CTA.
   * **Critical Video Effects:** 
     * Apply `mix-blend-darken` to the `<video>` element so its white background perfectly blends into the `#F5F5F7` page background.
     * Apply a CSS mask to the wrapper: `maskImage: 'radial-gradient(ellipse at center, black 65%, transparent 100%)'` to seamlessly fade out the extreme outer edges.
   * **Background Glow:** Place an absolute positioned `600x600px` white circle with `blur-[100px]` and `opacity-40` directly behind the video to give it a soft, ethereal backglow.
6. **Trust Indicators:**
   * 4 items: HIPAA Compliant, Secure Infrastructure, AI Assisted Documentation, Trusted by Clinics.
   * Icons: React Icons (`BsShieldCheck`, `BsLock`, `BsRobot`, `BsBuildings`).
   * Layout: Flex row, wrap on mobile, gap 8.
   * Styling: `text-sm text-[#5B5B65] font-medium`, centered beneath the video.

---

## 4. ANIMATIONS & MICRO-INTERACTIONS (Framer Motion)

* **Initial Page Load:**
  * Navbar: Slides down (`y: -20` to `0`), `opacity: 0` to `1` over `0.8s` easeOut.
  * Hero Content: Use `staggerChildren: 0.1` on a parent container. Each child (Badge, Heading, Subtitle, CTA, Video, Trust Indicators) fades up (`y: 20` to `0`, `opacity: 0` to `1`) over `0.8s` easeOut.
* **Continuous Floating Effect:**
  * The entire Hero Video container should gently float infinitely using Framer Motion: `animate={{ y: [0, -10, 0] }}`, `transition={{ duration: 6, ease: "easeInOut", repeat: Infinity }}`.
* **Hover States:**
  * Nav links: Underline expands from 0 to 100% width.
  * Buttons: Hover scales down slightly (`scale: 0.98`) or changes opacity/background color gently.

---

## 5. TECHNICAL DETAILS

* **SEO & Accessibility:**
  * Use proper `<nav>`, `<header>`, `<main>`, and `<h1>` tags.
  * Ensure buttons have `aria-label` where text isn't descriptive.
  * Video must have `autoPlay`, `muted`, `loop`, and `playsInline` attributes.
* **Performance:** 
  * Ensure the video is the only heavy asset. No heavy CSS frameworks outside of Tailwind.
* **Tailwind Config:** 
  * Add the custom fonts (`editorial`, `inter`) to the tailwind configuration extending the theme.

**Execution:** Provide all code in modular files (`Navbar.tsx`, `Hero.tsx`, `HeroVideo.tsx`, etc.), combining them in `App.tsx` or `index.tsx`. Ensure it looks pixel-perfect out of the box with zero additional configuration.
