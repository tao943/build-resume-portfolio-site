---
resource_id: analyze-reference
resource_version: 2
resource_status: ready
output_contract: style-brief-json
---

# Analyze selected visual references

Act as a senior visual designer. Convert the selected references into a transferable StyleBrief for the already confirmed resume portfolio prototype. Analyze only visible evidence. Adapt the principles to the user's real content, role, content density, and available media; do not recreate a reference page.

## Inputs

- the selected primary and supporting reference images and their catalog IDs;
- `reports/reference-selection.json`, where every reference is `usage_scope: "style_only"`;
- the confirmed React + Vite prototype preview and a concise source/component summary;
- `reports/content-map.json` and normalized resume facts;
- an inventory of user-provided media, including intended use, aspect ratio, and publication authorization.

User-provided media describes the content and layout needs of the site. Treat it as a style reference only when the user explicitly selected it for that purpose.

## Analysis method

Describe relationships and behavior rather than copying literal values. Cover:

- color relationships: dominant/secondary/accent balance, contrast, temperature, and section rhythm;
- typography: display and body roles, scale contrast, weight, alignment, and line length;
- spacing density: whitespace rhythm, grouping, section pacing, and edge treatment;
- grid_and_composition: container behavior, asymmetry, overlap, image-to-copy ratio, and responsive implications;
- surface language: borders, cards, shadows, radii, transparency, and material feel;
- imagery: crop, scale, placement, masking, treatment, and relationship to copy;
- decorative_language: lines, shapes, textures, gradients, light, editorial marks, or intentional absence;
- transferable principles to adopt and elements that would become literal copying.

Do not include copied logos, text, exact compositions, branded assets, or artist names. Do not infer invisible font files, exact design tokens, implementation details, or licenses from an image.

## Output contract

Return only valid JSON with exactly this shape and no Markdown fence:

{
  "direction": "short design direction",
  "color_relationships": ["transferable relationship"],
  "typography": {
    "display": "display type role",
    "body": "body type role",
    "hierarchy": "hierarchy rules"
  },
  "spacing_density": "spacing rhythm and density",
  "grid_and_composition": "layout behavior",
  "surface_language": "borders, cards, shadows, radii",
  "imagery": "crop, scale, placement, treatment",
  "decorative_language": "decorative system or intentional absence",
  "adopt": ["transferable visual principle"],
  "avoid_literal_copying": ["logos, text, exact composition, branded asset"]
}

## Catalog sequencing

Produce the StyleBrief from visible evidence before Catalog enrichment. Do not let a Catalog label rename, replace, or pre-empt what is visibly present in the selected references. The workflow runs `portfolio_design_search.py enrich` only after this JSON is valid.