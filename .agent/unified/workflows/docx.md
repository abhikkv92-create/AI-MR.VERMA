---
description: \"Desc\", name: \"Name\" } // All three required   })] }) ```  ### Page Breaks  ```javascript // CRITICAL: PageBreak must be inside a Paragraph new Paragraph({ children: [new PageBreak()] })  // Or use pageBreakBefore new Paragraph({ pageBreakBefore: true, children: [new TextRun(\"New page\")] }) ```  ### Table of Contents  ```javascript // CRITICAL: Headings must use HeadingLevel ONLY - no custom styles new TableOfContents(\"Table of Contents\", { hyperlink: true, headingStyleRange: \"1-3\" }) ```  ### Headers/Footers  ```javascript sections: [{   properties: {     page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } // 1440 = 1 inch   },   headers: {     default: new Header({ children: [new Paragraph({ children: [new TextRun(\"Header\")] })] })   },   footers: {     default: new Footer({ children: [new Paragraph({       children: [new TextRun(\"Page \"), new TextRun({ children: [PageNumber.CURRENT] })]     })] })   },   children: [/* content */] }] ```  ### Critical Rules for docx-js  - **Set page size explicitly** - docx-js defaults to A4; use US Letter (12240 x 15840 DXA) for US documents - **Landscape: pass portrait dimensions** - docx-js swaps width/height internally; pass short edge as `width`, long edge as `height`, and set `orientation: PageOrientation.LANDSCAPE` - **Never use `\n`** - use separate Paragraph elements - **Never use unicode bullets** - use `LevelFormat.BULLET` with numbering config - **PageBreak must be in Paragraph** - standalone creates invalid XML - **ImageRun requires `type`** - always specify png/jpg/etc - **Always set table `width` with DXA** - never use `WidthType.PERCENTAGE` (breaks in Google Docs) - **Tables need dual widths** - `columnWidths` array AND cell `width`, both must match - **Table width = sum of columnWidths** - for DXA, ensure they add up exactly - **Always add cell margins** - use `margins: { top: 80, bottom: 80, left: 120, right: 120 }` for readable padding - **Use `ShadingType.CLEAR`** - never SOLID for table shading - **TOC requires HeadingLevel only** - no custom styles on heading paragraphs - **Override built-in styles** - use exact IDs: \"Heading1\", \"Heading2\", etc. - **Include `outlineLevel`** - required for TOC (0 for H1, 1 for H2, etc.)
---

# docx Workflow

1. **Analyze Request**
   - Understand the user's specific need regarding **docx**.
   - Identify if the task involves docx best practices, specific patterns, or tool usage.

2. **Activate Skill**
   - Use the `view_file` tool to read the full instructions in:
     `E:\ABHINAV\AI KIT\.agent\skills\docx\SKILL.md`
   - **CRITICAL**: Read the `SKILL.md` file BEFORE proceeding. Do not assume you know the rules.

3. **Execute Strategy**
   - apply the principles and protocols defined in the skill.
   - If the skill provides specific tools or scripts, execute them as needed.

4. **Verify & refine**
   - Ensure the output aligns with the standards set in the skill documentation.

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/documentation-writer`.
