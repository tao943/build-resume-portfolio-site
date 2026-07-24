---
source_id: 03-cinematic-travel
original_number: 3
usage_scope: motion-recipe-source-only
---

3、# Wanderly - Premium Cinematic Travel Website Specification

**Description:** A cinematic travel website featuring an animated video hero and premium glassmorphism design.

This document serves as a comprehensive, production-ready specification to recreate the "Wanderly" travel and adventure website. It contains exact technical, visual, and architectural requirements.

## 1. Tech Stack & Architecture
- **Framework:** React 18+ with Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS (utility-first, responsive)
- **Animation:** Framer Motion (page transitions, scroll animations, micro-interactions)
- **Icons:** Lucide React (feather-style clean SVG icons)
- **Routing:** Single-page smooth scrolling anchor links.

## 2. Global Design System
### 2.1 Color Palette
- **Primary Dark (Backgrounds & Footer):** `#0A1A14` (Deep, rich forest green/black)
- **Primary Brand (Buttons, Accents):** `#1A4F36` (Emerald Green)
- **Primary Brand Hover:** `#226244` (Lighter Emerald)
- **Accent/Highlight:** `#FFC857` (Golden Yellow)
- **Background Light 1:** `#FFFFFF` (Pure White)
- **Background Light 2:** `#FAFAFA` (Off-white, used for alternating sections)
- **Background Light 3:** `#F9FAFB` (Tailwind `gray-50`)
- **Text Dark:** `#111827` (Tailwind `gray-900`)
- **Text Muted:** `#4B5563` (Tailwind `gray-600`) or `#6B7280` (`gray-500`)

### 2.2 Typography
- **Primary Font Family:** `Inter`, sans-serif
- **Headings (h1):** `font-bold`, `tracking-tight`, `leading-[1.05]`. Hero text uses sizes up to `88px` on large screens.
- **Section Headings (h2):** `font-bold`, `tracking-tight`, size `4xl` to `5xl`.
- **Body Text:** `font-light` to `font-normal`, `leading-relaxed`, size `lg` to `xl`.
- **Overline/Labels:** `uppercase`, `tracking-wider`, `text-xs` to `text-sm`, `font-semibold`.

### 2.3 Glassmorphism (Liquid Glass) Theme
Extensively used across the UI for overlays, cards, and navigation.
- **Base Glass:** `bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl`
- **Dark Glass (Nav):** `bg-black/40 backdrop-blur-md`
- **Text on Glass:** `text-white` for primary, `text-white/70` for secondary.

## 3. Section-by-Section Implementation Details

### 3.1 Global Navigation (`Navbar.tsx`)
- **Layout:** Fixed at top, `z-50`, max-width `7xl`, flex between.
- **Scroll Behavior:** Initially transparent with `py-6`. On scroll (>50px), morphs to `bg-black/40 backdrop-blur-md py-4` via Framer Motion.
- **Links:** Smooth scroll anchor links (`#destinations`, `#experiences`, etc.). Hover effects utilize a 0-width to full-width absolute white underline (`span`).
- **Mobile Menu:** Full-screen `bg-black/95 backdrop-blur-xl`, toggleable via Hamburger/X icon. Links stagger fade-in using `AnimatePresence`.

### 3.2 Hero Section (`Hero.tsx`)
- **Layout:** `h-[100vh] min-h-[700px]`, `flex items-center justify-center`.
- **Background:** Autoplaying, muted, looping, inline video (`object-cover`). Contains layered gradient overlays (`bg-gradient-to-r from-black/80` and `bg-gradient-to-t from-black/60`).
- **Scroll Parallax:** Video `y` position shifts `0%` to `20%` on scroll down. Entire Hero content `opacity` fades `1` to `0` using `useScroll` and `useTransform`.
- **Content:** Center aligned. 
  - Overline label: Plane icon + "Explore the World" in Golden Yellow `#FFC857`.
  - Main Title: "Journey Beyond the Ordinary" split into words, staggered fade-up animation.
  - Buttons: Solid Emerald button (`#1A4F36`) and a Glass Outline play button with a pinging border animation on hover.

### 3.3 Feature Grid (`FeatureCard.tsx`)
- **Layout:** Dedicated section immediately following Hero with `bg-[#0A1A14]` to seamlessly blend.
- **Card Design:** Single max-width glassmorphic card (`bg-white/10 backdrop-blur-md border border-white/20`) containing a 4-column grid.
- **Items:** 4 features (Handpicked Destinations, Unique Experiences, Trusted & Safe, 24/7 Support). Each has a glassmorphic circular icon container (`bg-white/10 border-white/20` with `#FFC857` icon) and white/translucent text. Hovering an item bumps it up (`y: -5`).

### 3.4 Destinations (`Destinations.tsx`)
- **Layout:** `bg-white` background, top/bottom padding 24/32. Bento-box CSS grid (`auto-rows-[300px]`).
- **Cards:** Relative containers with `overflow-hidden` and `rounded-[24px]`.
  - Image fills container (`object-cover`) and scales up `scale-110` on hover (duration `700ms`).
  - Dark gradient overlay intensifies on hover (`bg-black/20` to `bg-black/40`).
  - Text contents sit at bottom, translating up on hover to reveal description text.
- **Interactivity (Modal):** Clicking a card sets a `selectedDestination` state. Triggers a full-screen `AnimatePresence` modal:
  - **Backdrop:** `bg-black/60 backdrop-blur-sm`.
  - **Modal Card:** Spring animation (`type: "spring", damping: 25, stiffness: 300`), split 50/50 layout (image left, content right). Includes a "Book Now" CTA and close icon.

### 3.5 Experiences (`Experiences.tsx`)
- **Layout:** `bg-[#FAFAFA]`, 2-column grid.
- **Left Column:** Tall image (`h-[600px]`, `rounded-[32px]`). Contains a floating glassmorphic badge positioned `bottom-8 left-8 right-8` with an icon, title, and subtitle.
- **Right Column:** Text content, bullet points with circular emerald background icons, and a text-link CTA that expands arrow spacing on hover.

### 3.6 About/Brand Story (`About.tsx`)
- **Layout:** `bg-white`, centered minimal text block followed by a massive `h-[700px]` wide cinematic image container.
- **Image Container:** Has an absolute centered glassmorphic card (`bg-white/10 backdrop-blur-xl border border-white/20`) carrying the brand promise.

### 3.7 Plan My Trip (`PlanMyTrip.tsx`)
- **Layout:** Sits on a dark card (`bg-[#0A1A14]`) with a subtle, low-opacity (`20%`) airplane wing image background.
- **Form UI:** Glassmorphic wrapper (`bg-white/10 backdrop-blur-md`). 3 inline input fields (Destination, Dates, Guests) each wrapped in `bg-white/5` with Lucide icons.
- **CTA:** Bright Golden Yellow `#FFC857` submit button.

### 3.8 Travel Stories / Blog (`Blog.tsx`)
- **Layout:** `bg-[#FAFAFA]`, 3-column grid for latest articles.
- **Card Design:** Large image block (with hover `scale-105`), category in uppercase Emerald green, grey date, and bold 2-line clamped title.

### 3.9 Footer & Contact (`Contact.tsx` & `Footer.tsx`)
- **Contact Section:** `bg-[#FAFAFA]`. 2-column. Left side contains hover-interactive contact details (Mail, Phone, MapPin). Right side is a raised white card (`shadow-2xl`) containing a comprehensive inquiry form (Name, Email, Subject, Message, Send Button).
- **Footer Section:** `bg-[#0A1A14]`. 4-column layout (Brand + Newsletter, Nav Links, Contact Text). Newsletter input is a glass pill shape. Social links (Instagram, Twitter, Facebook) are bold, uppercase text links rather than icons.

## 4. Animation & Interaction Standards
- **Scroll Animations:** All new sections must utilize `<motion.div whileInView={{ opacity: 1, y: 0 }} initial={{ opacity: 0, y: 20 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }} />` to fade and slide up as they enter the viewport. Stagger children where applicable.
- **Hover States:** Buttons scale `1.02` on hover, `0.98` on tap. Icons inside CTA buttons translate right `translate-x-1`. Images inside cards zoom in slowly (`duration-700`).
- **Easing:** Default ease curve for primary transitions is `[0.16, 1, 0.3, 1]` (custom sleek decelerating curve).

## 5. Global CSS Requirements (`index.css`)
- Must include Tailwind directives.
- Must include `html { scroll-behavior: smooth; }` to ensure all anchor links glide smoothly.
- Optional base layer utility `.glass-card { @apply bg-white/10 backdrop-blur-md border border-white/20 shadow-lg; }`.

## 6. Development Workflow
1. Initialize Vite React TS project.
2. Install `framer-motion`, `lucide-react`, `tailwindcss`.
3. Configure `tailwind.config.js` to use `Inter` font.
4. Build bottom-up: generic UI -> complex sections -> wire up in `App.tsx`.
