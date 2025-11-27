# Screen Reference Images

This directory contains reference images for different screen types to help the AI generate more accurate and realistic screen visualizations.

## 📁 Directory Structure

The structure is organized by the single category **Lifestyle/Environmental**, broken down by openness factor (80, 95, 99).

```
screen_references/
└── lifestyle_environmental/
    ├── 80/
    │   └── master/     # Place reference images here
    ├── 95/
    │   └── master/     # Place reference images here
    └── 99/
        └── master/     # Place reference images here
```

## 📸 Image Requirements

### Quality Standards
- **Resolution**: Minimum 800x600, preferably 1200x800 or higher
- **Format**: JPG or PNG
- **Focus**: Clear, well-lit images showing screen texture and pattern
- **Angle**: Straight-on view of the screen mesh pattern

### Content Guidelines
- **Close-up shots** showing mesh pattern detail
- **Installed examples** showing screens on actual windows/doors
- **Different lighting conditions** (indoor, outdoor, various times of day)
- **Multiple angles** for each screen type

## 🤖 How AI Uses These References

The AI system uses these images to understand the texture, color, and opacity of the specific screen type and openness factor you are visualizing.

1. **Reference Selection**: The system looks for images in the `master` folder corresponding to the requested openness (80, 95, 99).
2. **Pattern Application**: The texture and opacity from the reference image are applied to the target window/door.

## 🚀 Getting Started

1. **Add your screen samples** to the appropriate `master` folder.
2. **Any image placed in the 'master' folder** will be used as a reference photo.
