#!/bin/bash
#
# Databricks Skills Installer
#
# Installs Databricks skills for Claude Code into your project.
# These skills teach Claude how to work with Databricks using MCP tools.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/databricks-skills/install_skills.sh | bash
#
# Or run locally:
#   ./install_skills.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/databricks-solutions/ai-dev-kit"
REPO_RAW_URL="https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main"
SKILLS_DIR=".claude/skills"

# Skills to install
SKILLS=(
    "dabs-writer"
    "databricks-python-sdk"
    "sdp-writer"
    "synthetic-data-generation"
)

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Databricks Skills Installer for Claude Code         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a git repo or project directory
if [ ! -d ".git" ] && [ ! -f "pyproject.toml" ] && [ ! -f "package.json" ] && [ ! -f "databricks.yml" ]; then
    echo -e "${YELLOW}Warning: This doesn't look like a project root directory.${NC}"
    echo -e "Current directory: $(pwd)"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create .claude/skills directory if it doesn't exist
if [ ! -d "$SKILLS_DIR" ]; then
    echo -e "${GREEN}Creating $SKILLS_DIR directory...${NC}"
    mkdir -p "$SKILLS_DIR"
fi

# Function to download a skill
download_skill() {
    local skill_name=$1
    local skill_dir="$SKILLS_DIR/$skill_name"
    local temp_dir=$(mktemp -d)

    echo -e "\n${BLUE}Processing skill: ${skill_name}${NC}"

    # Check if skill already exists
    if [ -d "$skill_dir" ]; then
        echo -e "${YELLOW}  Skill '$skill_name' already exists.${NC}"
        read -p "  Overwrite? (y/N): " overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            echo -e "  ${YELLOW}Skipped.${NC}"
            return 0
        fi
        rm -rf "$skill_dir"
    fi

    # Download skill files
    echo -e "  Downloading..."

    # Create skill directory
    mkdir -p "$skill_dir"

    # Download SKILL.md (required)
    if curl -sSL -f "${REPO_RAW_URL}/databricks-skills/${skill_name}/SKILL.md" -o "$skill_dir/SKILL.md" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Downloaded SKILL.md"
    else
        echo -e "  ${RED}✗${NC} Failed to download SKILL.md"
        rm -rf "$skill_dir"
        return 1
    fi

    # Try to download additional files (optional)
    # These are common additional files that skills might have
    for extra_file in "examples.md" "patterns.md" "reference.md" "migration-guide.md"; do
        if curl -sSL -f "${REPO_RAW_URL}/databricks-skills/${skill_name}/${extra_file}" -o "$skill_dir/${extra_file}" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Downloaded ${extra_file}"
        fi
    done

    # Clean up temp directory
    rm -rf "$temp_dir"

    echo -e "  ${GREEN}✓ Installed successfully${NC}"
    return 0
}

# Download each skill
echo -e "\n${GREEN}Installing Databricks skills...${NC}"
installed=0
failed=0

for skill in "${SKILLS[@]}"; do
    if download_skill "$skill"; then
        ((installed++))
    else
        ((failed++))
    fi
done

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "  Installed: ${installed} skills"
if [ $failed -gt 0 ]; then
    echo -e "  ${RED}Failed: ${failed} skills${NC}"
fi
echo ""
echo -e "${BLUE}Skills installed to: ${SKILLS_DIR}/${NC}"
echo ""
echo -e "Available skills:"
for skill in "${SKILLS[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo -e "  ${GREEN}✓${NC} $skill"
    fi
done
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Configure the Databricks MCP server in .claude/mcp.json"
echo -e "  2. Start Claude Code in your project directory"
echo -e "  3. Ask Claude to help with Databricks tasks!"
echo ""
echo -e "For MCP server setup, see:"
echo -e "  ${BLUE}${REPO_URL}${NC}"
echo ""
