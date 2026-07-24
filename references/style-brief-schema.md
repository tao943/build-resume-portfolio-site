# Style Brief Schema

Return valid JSON with these fields before applying a reference-derived style:

```json
{
  "direction": "short design direction",
  "color_relationships": ["relationship, not copied hex values"],
  "typography": {"display": "role", "body": "role", "hierarchy": "rules"},
  "spacing_density": "spacing rhythm and density",
  "grid_and_composition": "layout behavior",
  "surface_language": "borders, cards, shadows, radii",
  "imagery": "crop, scale, placement, treatment",
  "decorative_language": "lines, shapes, textures, or absence",
  "adopt": ["transferable visual principles"],
  "avoid_literal_copying": ["logos, text, exact compositions, branded assets"]
}
```

Base the brief on visible evidence from the selected references. Do not claim invisible design-system values. Adapt principles to the resume's content density and role rather than cloning the reference page.

Each ready reference manifest item must contain:

```json
{
  "id": "stable-id",
  "path": "relative-image-path.png",
  "role_tags": ["developer"],
  "visual_tags": ["editorial"],
  "source_note": "where the image came from",
  "license_note": "how it may be used",
  "aspect_ratio": "16:10",
  "available": true
}
```

Select references using role fit, content density, desired tone, and layout compatibility. Record all selected IDs in `reference-selection.json`.
