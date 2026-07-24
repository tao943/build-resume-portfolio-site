---
source_id: 10-biotech-video
original_number: 9
usage_scope: motion-recipe-source-only
---

9、Act as an award-winning designer and expert web developer. Your objective is to build a premium, highly responsive, and pixel-perfect hero section for a biotechnology company named "Genova Biosciences". 

Please follow the detailed specifications below to implement the design using React, TypeScript, Vite, and Vanilla CSS. 

## 1. Visual Design System

### Color Palette
- **Primary Brand (Blue)**: `#1a56db` (Used for highlighted text and primary actions)
- **Primary Brand Light**: `#eff6ff` (Used for icon backgrounds)
- **Text Primary (Dark Navy)**: `#0a192f` (Main headings and standard text)
- **Text Secondary (Slate Gray)**: `#475569` (Subheadings, descriptions, and labels)
- **Chip Background (Soft Blue)**: `#e0f2fe`
- **Chip Text (Deep Blue)**: `#0369a1`
- **Primary Button Background**: `#0c2b64`
- **Primary Button Hover**: `#133a80`
- **Secondary Button Background**: `rgba(255, 255, 255, 0.4)` (with backdrop blur)
- **Secondary Button Border**: `rgba(0, 0, 0, 0.1)`
- **Divider**: `rgba(0, 0, 0, 0.1)`
- **Background**: `#f8fafc`

### Typography
- **Font Family**: 'Inter', sans-serif (Import via Google Fonts)
- **Hero Title**: 4.5rem (72px), Font Weight: 700 (Bold), Line Height: 1.1, Letter Spacing: -0.02em.
- **Hero Description**: 1.15rem (18.4px), Font Weight: 400 (Regular), Line Height: 1.6, Color: Text Secondary.
- **Logo Text**: 1.5rem (24px), Font Weight: 700 (Bold), Line Height: 1.
- **Logo Subtext**: 0.65rem (10.4px), Font Weight: 500 (Medium), Letter Spacing: 2px, Uppercase.
- **Navigation Links**: 0.95rem (15.2px), Font Weight: 500 (Medium).
- **Button Text**: 0.95rem (15.2px), Font Weight: 500 (Medium).
- **Chip Text**: 0.75rem (12px), Font Weight: 600 (Semi-bold), Letter Spacing: 1px, Uppercase.

## 2. Layout Structure & Spacing

### Grid System & Container
- Use a fluid layout with Flexbox for primary alignment.
- The app container should span `min-height: 100vh` and `width: 100%`, with `overflow: hidden` to contain the absolute video background.

### Precise Spacing (Margins & Padding)
- **Navbar**: Padding `1.5rem` top/bottom, `4rem` left/right.
- **Nav Links Gap**: `2.5rem`.
- **Hero Content Container**: Max-width `800px`, padding `0 4rem`, margin-top `2rem`.
- **Title Margin Bottom**: `1.5rem`.
- **Description Margin Bottom**: `2.5rem`.
- **Hero Actions Margin Bottom**: `4rem`.
- **Buttons**: Padding `0.75rem 1.5rem`, Gap `0.5rem` (between text and icon).

## 3. Section-by-Section Content Hierarchy

### Background & Overlay
- An absolute-positioned `<video>` covering the entire screen (`object-fit: cover`, `z-index: -2`).
- An absolute-positioned `div` (`.video-overlay`) acting as a gradient fade (`z-index: -1`) to ensure text readability on the left side.
- Gradient: `linear-gradient(90deg, rgba(240, 248, 255, 1) 0%, rgba(240, 248, 255, 0.85) 40%, rgba(240, 248, 255, 0) 100%)`.

### Navbar
- **Left**: Logo container with a DNA icon and stacked text ("Genova" on top, "BIOSCIENCES" below).
- **Center**: Navigation links ("Solutions" with a chevron down icon, "Technology", "Research", "About Us", "Careers").
- **Right**: Primary "Contact Us" button with a right arrow icon.

### Hero Main Content (Left-Aligned)
- **Chip/Badge**: "INNOVATING LIFE SCIENCES" with a small blue dot indicator (`6px` by `6px`).
- **Headline**: "Advancing science.\nTransforming lives." (The word "Transforming" is highlighted in primary brand blue).
- **Description**: "Genova Biosciences is at the forefront of biotechnology, developing innovative solutions for a healthier tomorrow."
- **Actions**:
  - "Explore Our Solutions" (Primary button with right arrow).
  - "Watch Our Story" (Secondary glassmorphism button with a circled play icon).

## 4. UI Components & Styling Details

### Buttons
- **Shape**: Fully rounded (`border-radius: 9999px`).
- **Icons**: Utilize `lucide-react` for all icons.
- **Glassmorphism**: Secondary button should use a semi-transparent white background with `backdrop-filter: blur(8px)` and a subtle border.

## 5. Animations & Micro-Interactions

### Hover, Focus, & Active States
- **Nav Links**: Transition text color to Primary Brand Blue on hover (`transition: color 0.2s`).
- **Primary Buttons**: On hover, background darkens to `#133a80` and button shifts up slightly (`transform: translateY(-1px)`, `transition: all 0.2s ease`).
- **Secondary Buttons**: On hover, background opacity increases to `0.6` and border becomes slightly more visible.

### Entry Animations (Motion Design)
- Apply a subtle fade-in and slide-up animation (`@keyframes fadeInUp`) to the hero content elements (Chip, Title, Description, Buttons).
- Stagger the animations slightly (e.g., Title at `0.1s`, Description at `0.2s`, Buttons at `0.3s`) with an easing function (`cubic-bezier(0.4, 0, 0.2, 1)`) for a premium, dynamic feel.

## 6. Responsive Behavior (100% Responsiveness)

### Desktop (1024px and above)
- Default layout as specified above.

### Tablet (1024px to 768px)
- Reduce Hero Title font size to `3.5rem`.
- Adjust padding as necessary to prevent content overflow.

### Mobile (Below 768px)
- **Navbar**: Reduce padding to `1rem 2rem`. Hide main navigation links.
- **Hero Content**: Reduce padding to `0 2rem`, margin-top to `1rem`.
- **Hero Title**: Reduce font size to `2.5rem`.
- **Buttons**: Allow flex-wrap or stack buttons vertically if horizontal space is constrained.

## 7. Media & Assets

- **Background Video URL**: `https://strvid.nyc3.cdn.digitaloceanspaces.com/motionsite/dna_video.mp4` (Must auto-play, be muted, loop, and have `playsInline`).
- **Icons**: Use the following from `lucide-react`: `Dna`, `ChevronDown`, `ArrowRight`, `Play`.

## 8. Technical Implementation Details

### Frontend Architecture & File Structure
- Framework: **React** (Function components and hooks).
- Language: **TypeScript** (Strict typing).
- Bundler: **Vite**.
- File Structure:
  - `src/App.tsx`: Main component housing the layout and logic.
  - `src/index.css`: Vanilla CSS file containing all variables, resets, and styles.
  - `src/main.tsx`: Entry point.

### Dependencies
- `lucide-react`: For scalable, highly customizable SVG icons.

### Performance Optimization & SEO
- **Semantic HTML**: Use proper tags like `<nav>`, `<main>`, `<h1>`, `<p>`, and `<a>` for screen readers and SEO.
- **Video Optimization**: Ensure the video tag includes `muted`, `playsInline`, and `loop` for optimal performance without blocking the main thread. Provide fallback text within the `<video>` tag.
- **Accessibility**: Ensure sufficient color contrast between text and the overlay gradient. Add `aria-labels` to icon-only buttons or interactive elements if any.

Execute this precise specification and generate the complete, production-ready `App.tsx` and `index.css` code.
