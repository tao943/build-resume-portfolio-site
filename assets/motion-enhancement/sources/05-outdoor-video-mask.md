---
source_id: 05-outdoor-video-mask
original_number: 5
usage_scope: motion-recipe-source-only
---

5、You are an award-winning elite designer and expert web developer. Your objective is to build a premium, highly responsive, and visually stunning React + Tailwind CSS landing page from scratch. Recreate the following website with maximum accuracy.

## Complete Visual Design System

### Color Palette
- **Background (Page Outer Wrapper):** `#f3efe8`
- **Wander Blue (Theme):** `#7bb5cc`
- **Wander Orange (Accent/Action):** `#d9772b`
- **Wander Dark (Text/Icons):** `#1f3d47`
- **Wander Text (Subtext):** `#2a3b45`
- **Cutout Overlay:** `#f3efe8` (Matching background)
- **Hover States:** Bright Orange `#f97316` (Tailwind `orange-500`)

### Typography
- **Headings (H1, H2, H3, H4):** `Outfit`, ui-serif, Georgia, Cambria, "Times New Roman", Times, serif
- **Body / Sans:** `Inter`, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif
- **Main Headline:** 4xl (mobile), 5xl (tablet), 6xl (desktop), font weight 500, leading 1.05, tight tracking.
- **Subheadline:** lg (mobile), xl (tablet), max width ~28rem (`max-w-md`), text color 90% opacity of Wander Text.
- **Eyebrow Text ("Gear for every journey"):** Small (`sm`), bold, uppercase, widest tracking.

### Layout Structure & Grid System
- **Main App Wrapper:** Minimum height 100vh, flex column, items centered, with an outer padding of `p-4 md:p-6`.
- **Max Width Container:** The entire site contents are constrained to a maximum width of `1600px` to maintain a beautifully framed layout on ultrawide monitors.
- **Hero Container:** Inset rounded box spanning `h-[calc(100vh-2rem)] md:h-[calc(100vh-3rem)]`. 
- **Corners:** Large rounded corners (`rounded-[32px] md:rounded-[40px]`), overflow hidden, subtle drop shadow (`shadow-sm`), and a faint ring border (`ring-1 ring-black/5`).

## Section-by-Section Content and Hierarchy

### 1. Navigation Bar (Absolute Positioned inside Hero)
- **Position:** Absolute, top-0, left-0, right-0, z-50.
- **Padding:** `px-8 py-8 lg:px-16` to accommodate the large border radius of the hero.
- **Logo (Left):** `lucide-react` Mountain icon (`size={28}`) alongside text "WANDER" (font-bold, text-xl, uppercase, widest tracking). Text color `text-wander-dark`.
- **Links (Center):** Hidden on mobile, flex on large screens (`lg:flex`). Gap 8. Links: Camping, Hiking, Backpacks, Gear, Footwear, Accessories, Sale. Text color `text-wander-dark/90`. The "Sale" link is initially `text-wander-orange`.
- **Icons (Right):** Flex layout, gap 6. Search, User, ShoppingCart (with a small notification badge for "2" sitting at `-top-1.5 -right-2`, background orange).

### 2. Hero Section
- **Background Video:** Positioned at the bottom center of the container (`absolute bottom-0 left-1/2 -translate-x-1/2`). The video should NOT be stretched (`w-full md:w-auto` instead of `object-cover`).
  - **Source URL:** `https://strvid.nyc3.cdn.digitaloceanspaces.com/motionsite/travel_hike_bg_video_1.mp4`
  - **Masking / Blending:** To seamlessly sink the video into the blue background, apply a CSS mask gradient that heavily blurs the left, right, and top edges, while keeping the bottom edge perfectly sharp: `mask-image: radial-gradient(55% 100% at bottom, black 5%, transparent 90%)` (ensure both standard and Webkit properties are included).
  - **Playback:** Autoplay, looped, muted, playsInline. Playback rate set to `0.25` via React `useRef` for a slow, cinematic panning effect.
- **Content Alignment:** The text content wrapper must be exactly centered horizontally and vertically (`items-center justify-center text-center`), with a `max-w-3xl` and negative top margin (`-mt-22`) to optically pull it up slightly above absolute center.
- **Content Flow:** Eyebrow -> Main Headline -> Subheadline.
- **"Explore Category" Button:** Transparent background, 2px border of `wander-dark`, uppercase, tracking wide. Hover: background dark, text white.

### 3. "Shop Now" Inverted Cutout (Bottom Right)
- **Positioning:** Fixed to the absolute bottom-right of the Hero container (`bottom-0 right-0`).
- **Styling:** Background `#f3efe8`, rounded top-left (`rounded-tl-[40px]`), padding `pt-8 pl-10 pb-8 pr-10`, z-index 30.
- **Inverted Corners / Smooth Masking:** Use two absolute `w-10 h-10` `pointer-events-none` divs positioned to seamlessly merge the cutout into the container's straight edges using `radial-gradient(circle at 0 0, transparent 40px, #f3efe8 40px)`.
  - Corner 1 (top junction): `absolute bottom-full right-0`.
  - Corner 2 (left junction): `absolute bottom-0 right-full`.
- **Button:** 48x48px circle (`w-12 h-12`), background `black/5`, hover `black/10`, containing an `ArrowUpRight` icon.
- **Text:** "Shop Now" (text-lg, medium) over "Explore category >" (text-sm, 60% opacity).

## Hover, Focus, and Active States
- **Nav Links & Nav Icons:** Mouse hover state MUST transition to a bright orange highlight (`hover:text-orange-500 transition-colors`).
- **"Explore Category" Button:** Border and text invert to solid dark background and white text on hover.
- **Cutout Arrow Button:** Background darkens slightly from `bg-black/5` to `hover:bg-black/10`.

## Animations and Micro-interactions
- **Video Playback:** Set `videoRef.current.playbackRate = 0.25` inside a `useEffect` hook for slow-motion atmospheric motion.
- **Transitions:** All interactive hover states must use Tailwind's `transition-colors` with default duration and easing.

## Technical Implementation Details
- **Architecture:** React functional components with Tailwind CSS v4.
- **Dependencies:** `react`, `react-dom`, `@tailwindcss/vite`, `lucide-react` (for icons: Mountain, Search, User, ShoppingCart, ArrowUpRight).
- **CSS Strategy:** Pure Tailwind utility classes. Only use `index.css` to define the `@theme` variables (fonts, hex colors) and base body tags (`margin: 0; font-family`).
- **Responsiveness:** 100% responsive logic required using standard breakpoints (`sm`, `md`, `lg`, `xl`). Specifically handle font scaling on the H1 headline and visibility of the center nav links.

Follow this prompt entirely, missing no implementation details, particularly the inverted border radius technique for the cutout!
