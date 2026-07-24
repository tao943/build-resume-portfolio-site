# Poster-first video embed template

Use one local Poster as the permanent visual layer and progressively add a local video. The component keeps layout stable, hides failed video, and remains useful when no video has been supplied.

```tsx
type AdaptiveMotionMediaProps = { poster: string; video?: string };

export function AdaptiveMotionMedia({ poster, video }: AdaptiveMotionMediaProps) {
  const [failed, setFailed] = useState(false);
  return (
    <div data-motion-media className="motion-media">
      {video && !failed ? (
        <video autoPlay muted loop playsInline preload="metadata" poster={poster}
          onError={() => setFailed(true)} aria-hidden="true">
          <source src={video} />
        </video>
      ) : null}
      <img src={poster} alt="" aria-hidden="true" />
    </div>
  );
}
```

The same structure is valid in JSX after removing the prop type. Import media from local project assets; do not use remote MP4/WebM URLs.

```css
.motion-media {
  --motion-aspect: 16 / 9;
  --motion-fit: cover;
  position: relative;
  overflow: hidden;
  aspect-ratio: var(--motion-aspect);
}
.motion-media video,
.motion-media img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: var(--motion-fit);
}
.motion-media video { z-index: 1; }
@media (prefers-reduced-motion: reduce) {
  .motion-media video { display: none; }
}
```

Do not assign `currentTime`, opacity, clipping, or masks from scroll/pointer input. Keep text outside the media stacking context and protect contrast with a static gradient when needed.
