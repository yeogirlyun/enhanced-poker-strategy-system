# 🔧 **MEGA DOCUMENT GENERATOR TOOLS**

This directory contains powerful tools for creating comprehensive mega documents that combine multiple files into single, well-organized documentation packages.

## 🎯 **MAIN TOOL: Universal Mega Document Generator**

### `create_mega_document.py`

A highly configurable tool that can create different types of mega documents:

```bash
# General usage
python3 tools/create_mega_document.py <template> [options]

# List all available templates
python3 tools/create_mega_document.py --list-templates
```

### 📋 **Built-in Templates**

| Template | Description | Output | Use Case |
|----------|-------------|--------|----------|
| `bug_report` | Complete bug analysis with source code | `bug_report/COMPREHENSIVE_BUG_REPORT_WITH_SOURCE.md` | Debugging and issue resolution |
| `requirements` | Requirements specification with implementation | `req_requests/REQUIREMENTS_MEGA_DOCUMENT.md` | Feature planning and documentation |
| `architecture` | System architecture with code examples | `docs/ARCHITECTURE_MEGA_DOCUMENT.md` | Architecture reviews and onboarding |
| `feature` | Feature specification with implementation | `features/FEATURE_MEGA_DOCUMENT.md` | Feature development and testing |
| `mvu` | MVU architecture with infinite loop prevention | `mvu_docs/MVU_COMPLETE_IMPLEMENTATION.md` | MVU pattern implementation |

### 🚀 **Quick Examples**

```bash
# Create a bug report with all relevant source code
python3 tools/create_mega_document.py bug_report

# Create requirements document for planning
python3 tools/create_mega_document.py requirements

# Create architecture review document
python3 tools/create_mega_document.py architecture

# Create MVU implementation guide
python3 tools/create_mega_document.py mvu

# Use custom output location
python3 tools/create_mega_document.py bug_report --output ./custom_reports --filename MY_BUG_REPORT.md
```

### ⚙️ **Advanced Configuration**

You can create custom templates using JSON configuration:

```bash
# Use custom templates
python3 tools/create_mega_document.py hands_review_complete --config tools/mega_document_templates.json
```

#### Custom Template Format

```json
{
  "templates": {
    "my_template": {
      "title": "🎯 **MY CUSTOM DOCUMENT**",
      "description": "Custom document description",
      "output_dir": "my_output",
      "filename": "MY_DOCUMENT.md",
      "categories": [
        {
          "name": "CATEGORY NAME",
          "files": [
            "pattern1/**/*.py",
            "pattern2|keyword"
          ]
        }
      ]
    }
  }
}
```

#### File Pattern Syntax

- `**/*.py` - All Python files recursively
- `backend/ui/**/*.py` - Python files in specific directory tree
- `*BUG*.md` - Files with "BUG" in name
- `pattern|keyword` - Files matching pattern AND containing keyword

### 📊 **Features**

#### 🎨 **Professional Output**
- Syntax highlighting for all code files
- Organized categories with clear headers
- File size and statistics tracking
- Relative path information
- Generation timestamps

#### 🔧 **Smart File Handling**
- Automatic large file truncation
- Support for multiple file types
- Error handling for unreadable files
- Duplicate file removal
- Size optimization

#### 📁 **Flexible Organization**
- Template-based categorization
- Custom output directories
- Configurable filenames
- Multiple document types

#### 🚀 **Performance**
- Efficient file processing
- Memory-conscious design
- Progress tracking
- Statistics reporting

## 🎯 **SPECIFIC USE CASES**

### 📋 **Bug Report Generation**

When you encounter issues and need to create comprehensive bug reports:

```bash
# Standard bug report with all source code
python3 tools/create_mega_document.py bug_report

# Output goes to: bug_report/COMPREHENSIVE_BUG_REPORT_WITH_SOURCE.md
```

**Includes:**
- Bug analysis documentation
- Affected source code
- Configuration files
- Test cases
- Full system context

### 📋 **Requirements Documentation**

For feature planning and specification documentation:

```bash
# Complete requirements package
python3 tools/create_mega_document.py requirements

# Output goes to: req_requests/REQUIREMENTS_MEGA_DOCUMENT.md
```

**Includes:**
- Requirements specifications
- Architecture documentation
- Implementation source code
- Configuration and data files

### 📋 **Architecture Review**

For system architecture analysis and documentation:

```bash
# Full architecture review
python3 tools/create_mega_document.py architecture

# Output goes to: docs/ARCHITECTURE_MEGA_DOCUMENT.md
```

**Includes:**
- Architecture documentation
- Core implementation
- UI implementation
- Testing framework

### 📋 **MVU Implementation Guide**

For MVU pattern implementation and infinite loop prevention:

```bash
# Complete MVU guide
python3 tools/create_mega_document.py mvu

# Output goes to: mvu_docs/MVU_COMPLETE_IMPLEMENTATION.md
```

**Includes:**
- MVU architecture guide
- Complete implementation
- Model and types
- View rendering
- Infinite loop prevention

## 🔧 **COMMAND LINE OPTIONS**

```bash
Usage: create_mega_document.py <template> [options]

Positional Arguments:
  template              Document template (bug_report, requirements, etc.)

Options:
  -h, --help           Show help message
  -l, --list-templates List available templates
  -s, --source DIR     Source directory (default: current)
  -o, --output DIR     Output directory (default: template-specific)
  -f, --filename FILE  Output filename (default: template-specific)
  -c, --config FILE    Custom configuration file
  --max-lines N        Max lines from large files (default: 1000)
```

## 📈 **OUTPUT STATISTICS**

Each generated document includes:

- **File Count**: Total number of files included
- **Source Size**: Combined size of all source files
- **Output Size**: Final document size
- **Categories**: Number of categories processed
- **Generation Time**: When the document was created

## 🎯 **BEST PRACTICES**

### 📁 **Directory Organization**
- `bug_report/` - Bug analysis and resolution documents
- `req_requests/` - Requirements and planning documents
- `docs/` - Architecture and design documents
- `features/` - Feature specifications
- `mvu_docs/` - MVU implementation guides

### 🔧 **Template Selection**
- Use `bug_report` for debugging and issue resolution
- Use `requirements` for feature planning and documentation
- Use `architecture` for system reviews and onboarding
- Use `feature` for specific feature development
- Use `mvu` for MVU pattern implementation

### ⚙️ **Customization**
- Create custom templates for specific project needs
- Use configuration files for reusable templates
- Adjust file patterns to focus on relevant code
- Set appropriate output directories for organization

## 🚀 **INTEGRATION**

This tool integrates with the Poker project's architecture:

- **Follows Project Structure**: Understands backend/, ui/, docs/ organization
- **Respects Patterns**: Works with existing file patterns and conventions
- **Architecture Compliant**: Supports MVU, service container, and other patterns
- **Theme Aware**: Includes theme configuration and tokens

## 📋 **TROUBLESHOOTING**

### Common Issues

1. **Template Not Found**
   ```bash
   # List available templates
   python3 tools/create_mega_document.py --list-templates
   ```

2. **No Files Found**
   - Check file patterns in template configuration
   - Verify source directory contains expected files
   - Review pattern syntax (use `**` for recursive matching)

3. **Large Output Files**
   ```bash
   # Reduce max lines for large files
   python3 tools/create_mega_document.py template --max-lines 500
   ```

4. **Custom Templates**
   - Validate JSON syntax in configuration file
   - Check file path patterns
   - Verify output directory permissions

## 📋 **LEGACY TOOLS**

### `create_comprehensive_bug_report.py`

The original bug report generator (now superseded by the universal tool):

```bash
# Legacy usage (still supported)
python3 tools/create_comprehensive_bug_report.py --poker-default
```

**Note**: The universal `create_mega_document.py` provides all functionality of the legacy tool plus much more.

---

*This tool system provides a comprehensive solution for creating professional documentation packages that combine requirements, architecture, implementation, and testing into single, well-organized documents.*