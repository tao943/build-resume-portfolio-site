---
source_id: 02-dark-portfolio-stack
original_number: 2
usage_scope: motion-recipe-source-only
---

2、Act like an award-winning elite designer and expert web developer. Your objective is to build a premium, highly responsive, visually stunning, and interactive dark-themed portfolio website from scratch using React, Tailwind CSS, and Framer Motion. The resulting website should feel highly polished, expensive, and dynamic, employing smooth scroll transitions, micro-interactions, and 3D stacking effects.

Follow this detailed specification precisely to recreate the website.

---

## 1. Technical Stack & Architecture
- **Framework**: React.js (via Vite)
- **Styling**: Tailwind CSS
- **Animation Library**: Framer Motion (used for all scroll animations, layouts, and physics-based interactions)
- **Icons**: `lucide-react`
- **File Structure**:
  - `src/App.jsx` (Main container, renders Navbar, Hero, About, RecentWorks, Services, Footer)
  - `src/index.css` (Tailwind directives and global styles like dark background)
  - `src/components/` (Contains all UI sections)

## 2. Design System

### Color Palette
- **Primary Background**: `#0d1116` (Deep dark slate)
- **Secondary Background/Surface**: `#14181f` (Slightly lighter slate for cards)
- **Primary Accent**: `#00df8f` (Vibrant neon green / Cyberpunk green)
- **Gradient Accent**: `from-[#00df8f] to-[#00b373]`
- **Primary Text**: `#ffffff` (Pure white for headings)
- **Secondary Text**: `#9ca3af` (Gray-400 for paragraphs)
- **Borders/Dividers**: `rgba(255, 255, 255, 0.1)` (White with 10% opacity)

### Typography
- **Primary Font**: Modern sans-serif (e.g., 'Inter', 'Outfit', or 'Space Grotesk')
- **Headings (`font-display`)**: Bold, tight letter spacing (`tracking-tighter`), tight line heights (`leading-[0.9]`).
- **Body (`font-sans`)**: Regular to Medium, relaxed line height (`leading-relaxed`) for readability.
- **Labels/Tags**: Uppercase, heavily spaced (`tracking-widest`), small sizes (`text-sm` or `text-xs`).

---

## 3. Section Specifications

### A. Navigation Bar (`Navbar.jsx`)
- **Layout**: Fixed top, `w-full`, `h-24`, `z-50`.
- **Styling**: `bg-[#0f1115]/80` with `backdrop-blur-md` for a glass effect.
- **Logo**: Left-aligned "ZEDIAN" in white text with a neon green period (`<span className="text-[#00df8f]">.</span>`). Clicking the logo triggers a smooth scroll to the top of the page.
- **Links**: Center-right aligned list (`ABOUT`, `WORK`, `CONTACT`). Text is `text-sm`, `font-semibold`, `text-gray-300`, uppercase, with a hover transition to `#00df8f`. Clicking a link smoothly scrolls to the respective section ID.
- **Action Button**: Far right circular button with a neon green dot inside.

### B. Hero Section (`Hero.jsx`)
- **Layout**: `min-h-screen`, vertically centered, hidden overflow. Split into two columns on desktop (`lg:grid-cols-2`).
- **Background**: Deep background color `#0d1116` with a faint CSS grid overlay (`linear-gradient` 1px lines, 40px sizing, 3% opacity).
- **Typography Graphic**: A massive, barely visible text reading "DESIGN" (`text-[20vw]`, `opacity-[0.02]`) centered in the absolute background.
- **Left Column (Text Content)**:
  - Subheading: "UX/UI DESIGNER" with a small neon green dot indicator.
  - Main Heading: "DIGITAL" in solid white, followed by "EXPERIENCES." where "EXPERIENCES" uses an outline text effect (`text-transparent`, `WebkitTextStroke: '2px #00df8f'`) and the period is solid neon green.
  - Body: Short intro paragraph explaining the designer's craft.
  - CTA Buttons: 
    - "View My Work": Neon green gradient background, pill shape, white icon inside. Scale-up on hover.
    - "Contact Me": Dark surface, thin white border, green dot.
- **Right Column (Interactive ID Card)**:
  - Use `<motion.div>` with `drag`, `dragElastic={0.2}`, and `dragConstraints`.
  - Floating animation using `animate={{ y: [0, -15, 0], rotateZ: [-1, 1, -1] }}` on an infinite loop.
  - **Visual Design**: Looks like a physical ID badge. Dark gray rounded container with an inner border.
  - Contains a centered portrait image (use a placeholder AI portrait).
  - Bottom of the card features a dark gradient overlay revealing the text "Zedian." and "Lead UX/UI Designer".
  - A "Lanyard Strip" extends upwards from the card out of the screen using absolute positioning.

### C. About Section (`About.jsx`)
- **Layout**: `py-32`, split layout (`lg:grid-cols-2`). Section ID: `#about`.
- **Left Column**:
  - Heading: "DESIGNING WITH PURPOSE."
  - Text: Two paragraphs detailing a multidisciplinary background.
  - Stats Row: Two columns showing "20+ Awards" and "100% Commitment" separated by a thin vertical divider.
- **Right Column (My Toolkit)**:
  - A glassmorphism card (`bg-white/5`, `backdrop-blur-md`) containing an array of skill chips.
  - Skills: 'UI/UX Design', 'Figma', 'React.js', 'Framer Motion', 'Tailwind CSS', etc.
  - Hover states: Chips glow neon green on hover (`hover:border-[#00df8f] hover:text-[#00df8f] hover:shadow-[0_0_15px_rgba(0,223,143,0.3)]`).
  - Animation: Chips stagger fade-in when scrolled into view.

### D. Recent Works Section (`RecentWorks.jsx`)
- **Layout**: `py-32`. Top header features "RECENT WORKS" and a "View All Projects" button. Section ID: `#work`.
- **Core Mechanic**: A 3D Stacked Card Interactive Deck.
  - Render a grid split (`lg:grid-cols-12`). Left side (7 cols) holds the stack, right side (5 cols) holds project details.
  - **Left Side (The Stack)**: Absolute positioned cards stacked on top of each other. Uses React State `activeIdx`.
    - Active card (`diff === 0`) is at `y: 0`, `scale: 1`, front z-index.
    - Cards behind shift down (`y: diff * 35`), scale down (`scale: 1 - diff * 0.05`), and tilt backward (`rotateX: diff * 2`).
    - Interaction: Clicking the front card cycles it to the back. Clicking a back card pulls it instantly to the front.
    - Images: Use high-quality Unsplash architecture/design URLs.
  - **Right Side (Description Panel)**:
    - Anchored to the top (`items-start`). No background or borders, just raw text.
    - Uses `<AnimatePresence mode="wait">` to cleanly fade/slide text when the active project changes.
    - Displays: Category, Title, Description, Tags (array of pills), and an "Explore Project" button.
    - Bottom of the left column contains a navigation dot indicator mapping to the active card.

### E. Services Section (`Services.jsx`)
- **Layout**: Accordion style list inside a narrow container (`max-w-4xl`).
- **Heading**: Centered, "STAGES OF WEBSITE DEVELOPMENT" (with "DEVELOPMENT" using a transparent text stroke outline).
- **Accordion Items**: 
  - List of stages: BRIEFING, ANALYTICS, PROTOTYPING, DESIGN, ADAPTIVE, THE FINAL.
  - Each item has a number, large title, and a Plus/Minus toggle icon.
  - On click, use `<AnimatePresence>` and `<motion.div>` to smoothly animate height (`height: 'auto'`) to reveal descriptive text beneath.
  - Staggered `whileInView` fade-in for the list items upon scrolling.

### F. Footer Section (`Footer.jsx`)
- **Layout**: `pt-32 pb-10`, `border-t border-white/10`. Section ID: `#contact`.
- **Background Graphic**: Massive text reading "CONTACT" (`text-[25vw]`) anchored to the bottom with 5% opacity.
- **Top Row**: 
  - Left: "HOW CAN I HELP?" heading and bio paragraph. Email CTA button (solid white, black text, pill shape).
  - Right: Two-column grid of links ("Menu" and "Socials").
- **Bottom Row**: Copyright text ("© 2026 Zedian Portfolio. All rights reserved.") and privacy links.

---

## 4. Animations & Micro-Interactions
- **Scroll Triggers**: Every major text block and container must use `framer-motion`'s `whileInView={{ opacity: 1, y: 0 }}`. Use `viewport={{ once: true, margin: "-100px" }}` so animations trigger cleanly as elements enter the screen.
- **Staggering**: Use `transition={{ delay: index * 0.1, duration: 0.6 }}` when animating lists (like the skills chips or service items).
- **Physics**: The ID card in the Hero section MUST use `framer-motion` drag physics with `dragElastic={0.2}` and `dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}` so it snaps back naturally like a real hanging badge.
- **Transitions**: The 3D stack in Recent Works should use an easing curve `ease: [0.32, 0.72, 0, 1]` for luxurious, smooth card swapping.

## 5. Responsive Behavior
- **Mobile First**: Use default Tailwind utility classes for mobile layout.
- **Typography**: Scale fonts dynamically (e.g., `text-3xl sm:text-4xl md:text-5xl lg:text-6xl`).
- **Layouts**: Grids collapse to single columns on small screens (`grid-cols-1 md:grid-cols-2 lg:grid-cols-12`).
- **Stack UI**: Ensure the 3D card stack container height is responsive (`h-[340px] sm:h-[450px] md:h-[480px]`) so the navigation dots sit flush beneath the images on all screen sizes.

## 6. Image Assets
Use placeholder images from Unsplash. Example assets for the Recent Works array:
- `https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=800&auto=format&fit=crop`
- `https://images.unsplash.com/photo-1542204165-65bf26472b9b?q=80&w=800&auto=format&fit=crop`
- `https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800&auto=format&fit=crop`
- `https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop`
