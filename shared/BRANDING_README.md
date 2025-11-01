# Branding Assets

This directory contains shared branding assets for the Project Management Tools Suite.

## Image Assets

### Logo Files Needed

Replace the placeholder files with actual company branding:

1. **logo-placeholder.svg** - Main logo (SVG format recommended for scalability)
   - Recommended size: 200x60px or maintain similar aspect ratio
   - Format: SVG (preferred) or PNG with transparent background

2. **Additional logo variants to add:**
   - `logo-light.svg` - Light version for dark backgrounds
   - `logo-dark.svg` - Dark version for light backgrounds
   - `logo-icon.svg` - Icon-only version (square, 64x64px minimum)
   - `favicon.ico` - Browser favicon (32x32px)

### Background Images

Add any hero images or background graphics:
- `hero-bg.jpg` - Main landing page hero background
- `pattern-bg.svg` - Optional pattern overlay

### Application Icons

Consider adding specific icons for each tool:
- `cipp-icon.svg` - CIPP Analyzer icon
- `progress-icon.svg` - Progress Estimator icon
- Add more as new tools are added

## Color Palette

Update the CSS variables in `/shared/assets/css/common.css` with actual brand colors:

```css
:root {
    --brand-primary: #2c3e50;      /* Primary brand color */
    --brand-secondary: #3498db;    /* Secondary brand color */
    --brand-accent: #764ba2;       /* Accent color */
    --brand-success: #27ae60;      /* Success states */
    --brand-warning: #f39c12;      /* Warning states */
    --brand-danger: #e74c3c;       /* Error states */
}
```

## Typography

If the company uses specific fonts:

1. Add font files to `/shared/assets/fonts/` (create directory if needed)
2. Update font-family variables in `common.css`
3. Include @font-face declarations

## Usage Instructions

### In HTML Templates
```html
<link rel="stylesheet" href="/shared/assets/css/common.css">
<img src="/shared/assets/images/logo-placeholder.svg" alt="Company Logo" class="brand-logo">
```

### In Flask Applications
```python
# Serve shared assets
app.static_folder = 'shared/assets'
```

## File Formats

- **Logos**: SVG (preferred), PNG with transparency
- **Icons**: SVG (preferred), PNG
- **Photos**: JPG (compressed, optimized for web)
- **Backgrounds**: JPG or SVG patterns

## Optimization

Before deploying, optimize all images:
- Compress JPGs (80-85% quality)
- Optimize SVGs (remove unnecessary metadata)
- Use appropriate image sizes (no larger than needed)

## Design Guidelines

Maintain consistency across all tools:
- Use shared CSS variables for colors
- Follow common spacing and typography scales
- Apply consistent border radius and shadow styles
- Ensure accessibility (proper contrast ratios)

---

**IMPORTANT**: Update this README when adding new branding assets or making significant changes to the design system.
